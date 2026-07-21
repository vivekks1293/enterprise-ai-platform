import { Injectable, signal } from '@angular/core';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { LoadState } from '@shared/types/ui.types';
import { ApiError } from '@shared/models/api-error.model';

/**
 * Feature-local state, scoped to the Chat route (not root) via
 * ChatPage's `providers`. Deliberately a plain data bag — filtering
 * and derived values (pinned/recent split, selected conversation,
 * current message list) live in ChatFacade as computed signals, kept
 * out of here for the same reason ConversationsStateService keeps no
 * computed values either.
 *
 * `isWorkspaceLoading` (Phase 4 name, kept to avoid churn) now means
 * specifically "conversation list is loading" — see
 * `conversationDetailLoadState` for the separate main-pane loading
 * concern introduced in Phase 5.
 */
@Injectable()
export class ChatStateService {
  private readonly _conversations = signal<readonly ChatConversationSummary[]>([]);
  private readonly _messagesByConversation = signal<ReadonlyMap<string, readonly ChatMessage[]>>(new Map());
  private readonly _selectedConversationId = signal<string | null>(null);
  private readonly _searchTerm = signal<string>('');
  private readonly _sidebarCollapsed = signal<boolean>(false);
  private readonly _rightPanelCollapsed = signal<boolean>(false);
  private readonly _isWorkspaceLoading = signal<boolean>(true);
  private readonly _conversationDetailLoadState = signal<LoadState>('idle');
  private readonly _isSending = signal<boolean>(false);
  private readonly _error = signal<ApiError | null>(null);

  public readonly conversations = this._conversations.asReadonly();
  public readonly messagesByConversation = this._messagesByConversation.asReadonly();
  public readonly selectedConversationId = this._selectedConversationId.asReadonly();
  public readonly searchTerm = this._searchTerm.asReadonly();
  public readonly sidebarCollapsed = this._sidebarCollapsed.asReadonly();
  public readonly rightPanelCollapsed = this._rightPanelCollapsed.asReadonly();
  public readonly isWorkspaceLoading = this._isWorkspaceLoading.asReadonly();
  public readonly conversationDetailLoadState = this._conversationDetailLoadState.asReadonly();
  public readonly isSending = this._isSending.asReadonly();
  public readonly error = this._error.asReadonly();

  public setConversations(conversations: readonly ChatConversationSummary[]): void {
    this._conversations.set(conversations);
  }

  public addConversation(conversation: ChatConversationSummary): void {
    this._conversations.update((list) => [conversation, ...list]);
  }

  /** The backend's list/create/detail responses don't include a
   *  last-message snippet — ChatFacade derives one from actual message
   *  content it has loaded and calls this to reflect it in the sidebar. */
  public updateConversationPreview(id: string, preview: string): void {
    this._conversations.update((list) => list.map((c) => (c.id === id ? { ...c, preview } : c)));
  }

  public setMessagesForConversation(conversationId: string, messages: readonly ChatMessage[]): void {
    this._messagesByConversation.update((map) => {
      const next = new Map(map);
      next.set(conversationId, messages);
      return next;
    });
  }

  public hasCachedMessages(conversationId: string): boolean {
    return this._messagesByConversation().has(conversationId);
  }

  public appendMessage(conversationId: string, message: ChatMessage): void {
    const existing = this._messagesByConversation().get(conversationId) ?? [];
    this.setMessagesForConversation(conversationId, [...existing, message]);
  }

  public updateMessage(conversationId: string, messageId: string, patch: Partial<ChatMessage>): void {
    const existing = this._messagesByConversation().get(conversationId) ?? [];
    this.setMessagesForConversation(
      conversationId,
      existing.map((m) => (m.id === messageId ? { ...m, ...patch } : m))
    );
  }

  /** Appends a streamed chunk to an existing message's content in
   *  place — the exact mutation the Phase 4 mock reply already used,
   *  now driven by real StreamEvent chunks instead of a single canned string. */
  public appendToMessageContent(conversationId: string, messageId: string, chunk: string): void {
    const existing = this._messagesByConversation().get(conversationId) ?? [];
    this.setMessagesForConversation(
      conversationId,
      existing.map((m) => (m.id === messageId ? { ...m, content: m.content + chunk } : m))
    );
  }

  public setSelectedConversationId(id: string | null): void {
    this._selectedConversationId.set(id);
  }

  public setSearchTerm(term: string): void {
    this._searchTerm.set(term);
  }

  public toggleSidebarCollapsed(): void {
    this._sidebarCollapsed.update((collapsed) => !collapsed);
  }

  public toggleRightPanelCollapsed(): void {
    this._rightPanelCollapsed.update((collapsed) => !collapsed);
  }

  public setWorkspaceLoading(loading: boolean): void {
    this._isWorkspaceLoading.set(loading);
  }

  public setConversationDetailLoadState(state: LoadState): void {
    this._conversationDetailLoadState.set(state);
  }

  public setSending(sending: boolean): void {
    this._isSending.set(sending);
  }

  public setError(error: ApiError | null): void {
    this._error.set(error);
  }
}
