import { Injectable, signal } from '@angular/core';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';

/**
 * Feature-local state, scoped to the Chat route (not root) via
 * ChatPage's `providers`. Deliberately a plain data bag — filtering
 * and derived values (pinned/recent split, selected conversation,
 * current message list) live in ChatFacade as computed signals, kept
 * out of here for the same reason ConversationsStateService keeps no
 * computed values either.
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
  private readonly _isSending = signal<boolean>(false);

  public readonly conversations = this._conversations.asReadonly();
  public readonly messagesByConversation = this._messagesByConversation.asReadonly();
  public readonly selectedConversationId = this._selectedConversationId.asReadonly();
  public readonly searchTerm = this._searchTerm.asReadonly();
  public readonly sidebarCollapsed = this._sidebarCollapsed.asReadonly();
  public readonly rightPanelCollapsed = this._rightPanelCollapsed.asReadonly();
  public readonly isWorkspaceLoading = this._isWorkspaceLoading.asReadonly();
  public readonly isSending = this._isSending.asReadonly();

  public setConversations(conversations: readonly ChatConversationSummary[]): void {
    this._conversations.set(conversations);
  }

  public addConversation(conversation: ChatConversationSummary): void {
    this._conversations.update((list) => [conversation, ...list]);
  }

  public updateConversationPreview(id: string, preview: string, updatedAt: Date): void {
    this._conversations.update((list) =>
      list.map((c) => (c.id === id ? { ...c, preview, updatedAt } : c))
    );
  }

  public setMessagesForConversation(conversationId: string, messages: readonly ChatMessage[]): void {
    this._messagesByConversation.update((map) => {
      const next = new Map(map);
      next.set(conversationId, messages);
      return next;
    });
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

  public setSending(sending: boolean): void {
    this._isSending.set(sending);
  }
}
