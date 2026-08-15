import { Injectable, Signal, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ChatStateService } from '@features/chat/state/chat-state.service';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatRepository } from '@data/repositories/chat.repository';
import { generateId } from '@core/utils/id.util';
import { ROUTE_PATHS } from '@core/constants/app.constants';
import { NotificationService } from '@core/services/notification.service';
import { ApiError } from '@shared/models/api-error.model';

/**
 * The only thing ChatPage is allowed to inject. No component below
 * ChatPage in the tree talks to this Facade directly — see this
 * feature's Phase 4 architecture note for why.
 *
 * Phase 5 note on error display: the three REST calls this Facade
 * makes (create/list/get conversation) go through ApiClientService,
 * which means `error.interceptor.ts` ALREADY normalizes and toasts
 * their failures globally — this Facade only needs to update its own
 * loading/error signals for those, never call NotificationService
 * itself (that would double-toast). Streaming failures bypass the
 * HTTP interceptor entirely (StreamingClientService uses raw `fetch`),
 * so those ARE explicitly toasted here — the one asymmetry worth
 * remembering when extending this class.
 */
@Injectable()
export class ChatFacade {
  private readonly state = inject(ChatStateService);
  private readonly repository = inject(ChatRepository);
  private readonly router = inject(Router);
  private readonly notifications = inject(NotificationService);

  public readonly searchTerm = this.state.searchTerm;
  public readonly sidebarCollapsed = this.state.sidebarCollapsed;
  public readonly rightPanelCollapsed = this.state.rightPanelCollapsed;
  /** Conversation LIST loading (sidebar). */
  public readonly isConversationsLoading = this.state.isWorkspaceLoading;
  /** Conversation DETAIL loading (main pane) — distinct per spec's
   *  "Conversation List Loading" vs "Conversation Detail Loading". */
  public readonly conversationDetailLoadState = this.state.conversationDetailLoadState;
  public readonly isSending = this.state.isSending;
  public readonly error = this.state.error;
  public readonly selectedConversationId = this.state.selectedConversationId;

  private readonly filteredConversations = computed(() => {
    const term = this.state.searchTerm().trim().toLowerCase();
    const list = this.state.conversations();
    if (!term) {
      return list;
    }
    return list.filter((c) => c.title.toLowerCase().includes(term));
  });

  // Always empty today — the backend has no pinning concept yet (see
  // ChatConversationSummary.pinned doc comment). Kept so the sidebar's
  // Pinned/Recent split needs no changes if pinning is added later.
  public readonly pinnedConversations = computed(() => this.filteredConversations().filter((c) => c.pinned));
  public readonly recentConversations = computed(() => this.filteredConversations().filter((c) => !c.pinned));

  public readonly selectedConversation: Signal<ChatConversationSummary | null> = computed(() => {
    const id = this.state.selectedConversationId();
    return this.state.conversations().find((c) => c.id === id) ?? null;
  });

  public readonly messages: Signal<readonly ChatMessage[]> = computed(() => {
    const id = this.state.selectedConversationId();
    if (!id) {
      return [];
    }
    return this.state.messagesByConversation().get(id) ?? [];
  });

  /** Subscription to the in-flight prompt stream, if any — held so
   *  `stopGeneration()` can unsubscribe it, which triggers
   *  StreamingClientService's AbortController teardown automatically. */
  private activeStreamSubscription?: Subscription;

  /** Loads the conversation list for the sidebar. Called once from
   *  ChatPage's ngOnInit — independent of which conversation (if any)
   *  is currently open, since ChatPage is reused across
   *  /chat/:id1 → /chat/:id2 navigations. */
  public loadConversations(): void {
    this.state.setWorkspaceLoading(true);
    this.repository.listConversations().subscribe({
      next: (conversations) => {
        // Backend list responses carry no last-message snippet — merge
        // in previews we've already derived locally for any conversation
        // whose messages we have cached, so this refresh (called after
        // every send, per finalizeAssistantMessage) doesn't blank them out.
        this.state.setConversations(this.withCachedPreviews(conversations));
        this.state.setWorkspaceLoading(false);
      },
      error: (error: ApiError) => {
        // Already toasted by error.interceptor.ts — just reflect state here.
        this.state.setError(error);
        this.state.setWorkspaceLoading(false);
      }
    });
  }

  /**
   * Loads one conversation's detail (header + messages) from the
   * backend. Called reactively by ChatPage whenever the
   * `:conversationId` route param changes.
   *
   * Session-local cache: if this conversation's messages are already
   * in `messagesByConversation` (visited earlier this session, or just
   * created), this is a pure selection switch with no network call —
   * standard chat-app behavior, not a violation of "history always
   * comes from the backend" (the cached data DID come from the backend;
   * this just avoids re-fetching it every time the user flips back to
   * a conversation they already opened).
   */
  public loadConversation(conversationId: string): void {
    this.state.setSelectedConversationId(conversationId);

    if (this.state.hasCachedMessages(conversationId)) {
      return;
    }

    this.state.setConversationDetailLoadState('loading');
    this.repository.getConversation(conversationId).subscribe({
      next: ({ messages }) => {
        this.state.setMessagesForConversation(conversationId, messages);
        this.syncPreviewFromMessages(conversationId);
        this.state.setConversationDetailLoadState('success');
      },
      error: (error: ApiError) => {
        // Already toasted by error.interceptor.ts — just reflect state here.
        this.state.setError(error);
        this.state.setConversationDetailLoadState('error');
      }
    });
  }

  /** Called by ChatPage when the route has no `:conversationId` (bare /chat). */
  public deselectConversation(): void {
    this.state.setSelectedConversationId(null);
    this.state.setConversationDetailLoadState('idle');
  }

  /** Explicit "New conversation" button — always creates a blank,
   *  generically-titled conversation and navigates to it. Distinct from
   *  the implicit auto-create inside `sendMessage()`, which titles the
   *  conversation from the user's first prompt instead. */
  public startNewConversation(): void {
    this.repository.createConversation('New conversation').subscribe({
      next: (summary) => {
        this.state.addConversation(summary);
        void this.router.navigateByUrl(`/${ROUTE_PATHS.chat}/${summary.id}`);
      },
      error: (error: ApiError) => {
        this.state.setError(error);
      }
    });
  }

  /** Sidebar conversation click. Navigating (rather than setting local
   *  state directly) makes the URL the source of truth for which
   *  conversation is open — bookmarkable, and consistent with how
   *  `startNewConversation()` already behaves. `ChatPage`'s route-param
   *  effect is what actually triggers `loadConversation()`. */
  public selectConversation(id: string): void {
    void this.router.navigateByUrl(`/${ROUTE_PATHS.chat}/${id}`);
  }

  public setSearchTerm(term: string): void {
    this.state.setSearchTerm(term);
  }

  public toggleSidebar(): void {
    this.state.toggleSidebarCollapsed();
  }

  public toggleRightPanel(): void {
    this.state.toggleRightPanelCollapsed();
  }

  public sendMessage(text: string): void {
    const trimmed = text.trim();
    if (!trimmed || this.state.isSending()) {
      return;
    }

    const existingId = this.state.selectedConversationId();
    if (existingId) {
      this.dispatchPrompt(existingId, trimmed);
      return;
    }

    // No conversation open yet — create one first, titled from the
    // prompt itself, then send against the new id. Mirrors the Phase 4
    // mock behavior of implicitly starting a conversation when the
    // user types without selecting one first.
    this.state.setSending(true);
    const seedTitle = trimmed.length > 60 ? `${trimmed.slice(0, 60)}…` : trimmed;

    this.repository.createConversation(seedTitle).subscribe({
      next: (summary) => {
        this.state.addConversation(summary);
        this.state.setSelectedConversationId(summary.id);
        void this.router.navigateByUrl(`/${ROUTE_PATHS.chat}/${summary.id}`);
        this.dispatchPrompt(summary.id, trimmed);
      },
      error: (error: ApiError) => {
        this.state.setSending(false);
        this.state.setError(error);
      }
    });
  }

  /**
   * The exact seam Phase 4 was built around: append the user message,
   * append an empty `status: 'streaming'` assistant placeholder, then
   * fill that same message's content in place as chunks arrive. What's
   * changed since Phase 4/5: the backend now sends real SSE
   * (`token`/`citations`/`complete` events) instead of raw text
   * chunks, so this consumes typed `ChatStreamEvent`s from
   * ChatRepository rather than raw `StreamEvent<string>` — the
   * append-in-place pattern itself is unchanged.
   *
   * IDs generated here (`generateId()`) are client-local, rendering-only
   * identifiers — never sent to the backend, never treated as
   * authoritative. They get superseded by the backend's real message
   * IDs the next time this conversation is loaded fresh via
   * `getConversation()` (e.g. a future session, or a forced reload).
   */
  private dispatchPrompt(conversationId: string, prompt: string): void {
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: prompt,
      createdAt: new Date(),
      status: 'complete'
    };
    this.state.appendMessage(conversationId, userMessage);
    this.syncPreviewFromMessages(conversationId);

    const assistantMessageId = generateId();
    const placeholder: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      createdAt: new Date(),
      status: 'streaming'
    };
    this.state.appendMessage(conversationId, placeholder);
    this.state.setSending(true);
    this.state.setError(null);

    this.activeStreamSubscription = this.repository.streamPrompt(conversationId, prompt).subscribe({
      next: (event) => {
        switch (event.kind) {
          case 'token':
            this.state.appendToMessageContent(conversationId, assistantMessageId, event.content);
            break;
          case 'citations':
            // Attaches to the SAME assistant message being streamed —
            // never creates a new message. Citation UI itself is a
            // future task; this just gets the data into state.
            this.state.updateMessage(conversationId, assistantMessageId, { citations: event.citations });
            break;
          case 'complete':
            this.finalizeAssistantMessage(conversationId, assistantMessageId);
            break;
        }
      },
      error: (error: ApiError) => this.handleStreamError(conversationId, assistantMessageId, error),
      // Backup path: if the connection closes without an explicit
      // `complete` event reaching us first (e.g. a future backend
      // variant, or a network-level close), this still finalizes the
      // message rather than leaving it stuck in 'streaming' forever.
      // finalizeAssistantMessage() is idempotent, so this is a no-op
      // if `complete` already fired.
      complete: () => this.finalizeAssistantMessage(conversationId, assistantMessageId)
    });
  }

  /** Stops an in-flight generation. Per spec: leaves the user message
   *  intact, finalizes whatever partial content the assistant message
   *  already has rather than creating a duplicate message. */
  public stopGeneration(): void {
    this.activeStreamSubscription?.unsubscribe();
    this.activeStreamSubscription = undefined;

    const conversationId = this.state.selectedConversationId();
    if (!conversationId) {
      this.state.setSending(false);
      return;
    }
    const messages = this.state.messagesByConversation().get(conversationId) ?? [];
    const inFlight = [...messages].reverse().find((m) => m.role === 'assistant' && m.status === 'streaming');
    if (inFlight) {
      this.state.updateMessage(conversationId, inFlight.id, { status: 'complete' });
    }
    this.state.setSending(false);
  }

  private finalizeAssistantMessage(conversationId: string, messageId: string): void {
    if (!this.state.isSending()) {
      return; // already finalized via stopGeneration() or a prior error
    }
    this.state.updateMessage(conversationId, messageId, { status: 'complete' });
    this.syncPreviewFromMessages(conversationId);
    this.state.setSending(false);
    // Refresh sidebar ordering/updated_at now that this conversation had activity.
    this.loadConversations();
  }

  /** The backend doesn't return a last-message snippet anywhere — this
   *  derives one from actual message content already loaded/appended
   *  locally and reflects it in the sidebar. Skips the in-flight empty
   *  assistant placeholder so the preview doesn't briefly blank out
   *  between "user sent" and "assistant replied". */
  private syncPreviewFromMessages(conversationId: string): void {
    const messages = this.state.messagesByConversation().get(conversationId) ?? [];
    for (let i = messages.length - 1; i >= 0; i--) {
      const content = messages[i].content.trim();
      if (content.length > 0) {
        this.state.updateConversationPreview(conversationId, content);
        return;
      }
    }
  }

  /** Preserves previews already derived this session when a fresh
   *  conversation list comes back from the backend (which never
   *  includes a preview field itself) — otherwise every list refresh
   *  (called after each send) would blank previews back out. */
  private withCachedPreviews(
    conversations: readonly ChatConversationSummary[]
  ): readonly ChatConversationSummary[] {
    return conversations.map((conversation) => {
      const cached = this.state.messagesByConversation().get(conversation.id);
      if (!cached) {
        return conversation;
      }
      for (let i = cached.length - 1; i >= 0; i--) {
        const content = cached[i].content.trim();
        if (content.length > 0) {
          return { ...conversation, preview: content };
        }
      }
      return conversation;
    });
  }

  private handleStreamError(conversationId: string, assistantMessageId: string, error: ApiError): void {
    this.state.updateMessage(conversationId, assistantMessageId, { status: 'error' });
    this.state.setSending(false);
    this.state.setError(error);
    // Streaming bypasses the HTTP interceptor chain entirely, so unlike
    // the REST methods above, this toast is NOT automatic — it has to
    // happen here.
    this.notifications.notify(error.message, 'error');
  }
}
