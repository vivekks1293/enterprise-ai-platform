import { DestroyRef, Injectable, computed, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { timer } from 'rxjs';
import { ChatStateService } from '@features/chat/state/chat-state.service';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { MOCK_ASSISTANT_REPLIES, MOCK_CONVERSATIONS, MOCK_MESSAGES } from '@features/chat/services/chat.mock';
import { generateId } from '@core/utils/id.util';

/**
 * The only thing ChatPage is allowed to inject. No component below
 * ChatPage in the tree talks to this Facade directly — they receive
 * plain inputs/outputs from ChatPage via ConversationWorkspace. See
 * this phase's architecture note for why that prop-drilling is a
 * deliberate trade-off here.
 *
 * `sendMessage()` is the seam future streaming replaces: it appends a
 * user message, appends a placeholder assistant message with
 * `status: 'streaming'`, then fills that same message's content in
 * place after a delay. A future StreamingClientService integration
 * swaps the `timer(...).subscribe(...)` body for
 * `streamingClient.connect(...)` — MessageBubble's rendering and every
 * signal this Facade exposes stay exactly as they are today.
 */
@Injectable()
export class ChatFacade {
  private readonly state = inject(ChatStateService);
  private readonly destroyRef = inject(DestroyRef);

  public readonly searchTerm = this.state.searchTerm;
  public readonly sidebarCollapsed = this.state.sidebarCollapsed;
  public readonly rightPanelCollapsed = this.state.rightPanelCollapsed;
  public readonly isWorkspaceLoading = this.state.isWorkspaceLoading;
  public readonly isSending = this.state.isSending;
  public readonly selectedConversationId = this.state.selectedConversationId;

  private readonly filteredConversations = computed(() => {
    const term = this.state.searchTerm().trim().toLowerCase();
    const list = this.state.conversations();
    if (!term) {
      return list;
    }
    return list.filter((c) => c.title.toLowerCase().includes(term));
  });

  public readonly pinnedConversations = computed(() => this.filteredConversations().filter((c) => c.pinned));
  public readonly recentConversations = computed(() => this.filteredConversations().filter((c) => !c.pinned));

  public readonly selectedConversation = computed<ChatConversationSummary | null>(() => {
    const id = this.state.selectedConversationId();
    return this.state.conversations().find((c) => c.id === id) ?? null;
  });

  public readonly messages = computed<readonly ChatMessage[]>(() => {
    const id = this.state.selectedConversationId();
    if (!id) {
      return [];
    }
    return this.state.messagesByConversation().get(id) ?? [];
  });

  /**
   * Simulates an initial "fetch" so the loading-state UX matches what
   * a real conversation-history request will look like once the
   * backend endpoint exists — same pattern as ConversationsFacade,
   * just with a timer instead of an HTTP call underneath it.
   */
  public initWorkspace(): void {
    this.state.setWorkspaceLoading(true);

    timer(400)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.state.setConversations(MOCK_CONVERSATIONS);
        for (const [conversationId, messages] of MOCK_MESSAGES) {
          this.state.setMessagesForConversation(conversationId, messages);
        }
        const first = MOCK_CONVERSATIONS[0];
        if (first) {
          this.state.setSelectedConversationId(first.id);
        }
        this.state.setWorkspaceLoading(false);
      });
  }

  public selectConversation(id: string): void {
    this.state.setSelectedConversationId(id);
  }

  public startNewConversation(): void {
    const conversation: ChatConversationSummary = {
      id: generateId(),
      title: 'New conversation',
      preview: 'No messages yet',
      updatedAt: new Date(),
      pinned: false
    };
    this.state.addConversation(conversation);
    this.state.setSelectedConversationId(conversation.id);
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

    let conversationId = this.state.selectedConversationId();
    if (!conversationId) {
      this.startNewConversation();
      conversationId = this.state.selectedConversationId();
    }
    if (!conversationId) {
      return;
    }

    const now = new Date();
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: trimmed,
      createdAt: now,
      status: 'complete'
    };
    this.state.appendMessage(conversationId, userMessage);
    this.state.updateConversationPreview(conversationId, trimmed, now);

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

    const finalConversationId = conversationId;
    const reply = MOCK_ASSISTANT_REPLIES[Math.floor(Math.random() * MOCK_ASSISTANT_REPLIES.length)];

    timer(900)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.state.updateMessage(finalConversationId, assistantMessageId, {
          content: reply,
          status: 'complete'
        });
        this.state.updateConversationPreview(finalConversationId, reply, new Date());
        this.state.setSending(false);
      });
  }
}
