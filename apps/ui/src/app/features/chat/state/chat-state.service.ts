import { Injectable, signal } from '@angular/core';
import { ChatMessage, ConversationSummary } from '@data/models/chat.dto';

@Injectable({ providedIn: 'root' })
export class ChatStateService {
  public readonly conversations = signal<readonly ConversationSummary[]>([]);
  public readonly selectedConversationId = signal<string | null>(null);
  public readonly messages = signal<readonly ChatMessage[]>([]);
  public readonly isConversationsLoading = signal<boolean>(false);
  public readonly isMessagesLoading = signal<boolean>(false);
  public readonly isSending = signal<boolean>(false);
  public readonly isStreaming = signal<boolean>(false);
  public readonly searchTerm = signal<string>('');

  public reset(): void {
    this.conversations.set([]);
    this.selectedConversationId.set(null);
    this.messages.set([]);
    this.isConversationsLoading.set(false);
    this.isMessagesLoading.set(false);
    this.isSending.set(false);
    this.isStreaming.set(false);
    this.searchTerm.set('');
  }

  public setConversations(items: readonly ConversationSummary[]): void {
    this.conversations.set(items);
  }

  public addConversation(item: ConversationSummary): void {
    this.conversations.update((list) => [item, ...list.filter((c) => c.id !== item.id)]);
  }

  public removeConversation(id: string): void {
    this.conversations.update((list) => list.filter((c) => c.id !== id));
    if (this.selectedConversationId() === id) {
      this.selectedConversationId.set(null);
      this.messages.set([]);
    }
  }

  public setSelectedId(id: string | null): void {
    this.selectedConversationId.set(id);
  }

  public setMessages(messages: readonly ChatMessage[]): void {
    this.messages.set(messages);
  }

  public addMessage(message: ChatMessage): void {
    this.messages.update((list) => [...list, message]);
  }

  public updateLastAssistantMessage(updater: (msg: ChatMessage) => ChatMessage): void {
    this.messages.update((list) => {
      const copy = [...list];
      for (let i = copy.length - 1; i >= 0; i--) {
        if (copy[i].role === 'assistant') {
          copy[i] = updater(copy[i]);
          break;
        }
      }
      return copy;
    });
  }
}

