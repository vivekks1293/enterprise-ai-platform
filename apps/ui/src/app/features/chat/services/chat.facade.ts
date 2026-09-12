import { Injectable, inject, computed } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ChatStateService } from '../state/chat-state.service';
import { ChatRepository } from '@data/repositories/chat.repository';
import { NotificationService } from '@core/services/notification.service';
import { ChatMessage, ConversationSummary, Citation } from '@data/models/chat.dto';

@Injectable({ providedIn: 'root' })
export class ChatFacade {
  private readonly state = inject(ChatStateService);
  private readonly repository = inject(ChatRepository);
  private readonly router = inject(Router);
  private readonly toast = inject(NotificationService);

  private streamSub?: Subscription;

  public readonly conversations = this.state.conversations;
  public readonly selectedConversationId = this.state.selectedConversationId;
  public readonly messages = this.state.messages;
  public readonly isConversationsLoading = this.state.isConversationsLoading;
  public readonly isMessagesLoading = this.state.isMessagesLoading;
  public readonly isSending = this.state.isSending;
  public readonly isStreaming = this.state.isStreaming;
  public readonly searchTerm = this.state.searchTerm;

  public readonly activeConversation = computed(() => {
    const id = this.state.selectedConversationId();
    if (!id) return null;
    return this.state.conversations().find((c) => c.id === id) ?? null;
  });

  public readonly filteredConversations = computed(() => {
    const term = this.state.searchTerm().trim().toLowerCase();
    const list = this.state.conversations();
    if (!term) return list;
    return list.filter((c) => c.title.toLowerCase().includes(term));
  });

  public loadConversations(): void {
    this.state.isConversationsLoading.set(true);
    this.repository.listConversations().subscribe({
      next: (items) => {
        this.state.setConversations(items);
        this.state.isConversationsLoading.set(false);
      },
      error: () => {
        this.state.isConversationsLoading.set(false);
        this.toast.error('Failed to load conversation history');
      }
    });
  }

  public selectConversation(id: string): void {
    if (this.state.selectedConversationId() === id) return;
    this.stopGeneration();

    this.state.setSelectedId(id);
    this.state.isMessagesLoading.set(true);

    this.repository.getConversation(id).subscribe({
      next: ({ messages }) => {
        this.state.setMessages(messages);
        this.state.isMessagesLoading.set(false);
      },
      error: () => {
        this.state.isMessagesLoading.set(false);
        this.toast.error('Failed to load conversation messages');
      }
    });
  }

  public startNewChat(): void {
    this.stopGeneration();
    this.state.setSelectedId(null);
    this.state.setMessages([]);
    if (this.router.url !== '/chat') {
      this.router.navigate(['/chat']);
    }
  }

  public resetState(): void {
    this.stopGeneration();
    this.state.reset();
  }

  public sendPrompt(text: string): void {
    const prompt = text.trim();
    if (!prompt || this.state.isSending() || this.state.isStreaming()) {
      return;
    }

    const currentId = this.state.selectedConversationId();
    if (!currentId) {
      // Create new conversation first, using prompt snippet as title
      const title = prompt.slice(0, 35) + (prompt.length > 35 ? '...' : '');
      this.state.isSending.set(true);

      this.repository.createConversation(title).subscribe({
        next: (created) => {
          const newSummary: ConversationSummary = {
            id: created.id,
            title: created.title,
            createdAt: created.created_at,
            updatedAt: created.updated_at
          };
          this.state.addConversation(newSummary);
          this.state.setSelectedId(created.id);
          this.dispatchUserAndAssistantMessages(created.id, prompt);
          this.router.navigate(['/chat', created.id], { replaceUrl: true });
        },
        error: () => {
          this.state.isSending.set(false);
          this.toast.error('Could not initiate a new conversation');
        }
      });
    } else {
      this.dispatchUserAndAssistantMessages(currentId, prompt);
    }
  }

  private dispatchUserAndAssistantMessages(conversationId: string, prompt: string): void {
    const userMsg: ChatMessage = {
      id: 'usr-' + Date.now(),
      role: 'user',
      content: prompt,
      createdAt: new Date().toISOString()
    };

    const assistantMsg: ChatMessage = {
      id: 'asst-' + Date.now(),
      role: 'assistant',
      content: '',
      createdAt: new Date().toISOString(),
      isStreaming: true,
      citations: []
    };

    this.state.addMessage(userMsg);
    this.state.addMessage(assistantMsg);

    this.state.isSending.set(true);
    this.state.isStreaming.set(true);

    this.streamSub = this.repository.streamPrompt(conversationId, prompt).subscribe({
      next: (event) => {
        if (event.type === 'token' && event.content) {
          this.state.updateLastAssistantMessage((msg) => ({
            ...msg,
            content: msg.content + event.content!
          }));
        } else if (event.type === 'citations' && event.citations) {
          this.state.updateLastAssistantMessage((msg) => ({
            ...msg,
            citations: event.citations
          }));
        } else if (event.type === 'complete') {
          this.finalizeStream();
        }
      },
      error: () => {
        this.state.updateLastAssistantMessage((msg) => ({
          ...msg,
          content: msg.content || 'An error occurred while generating a response.',
          isStreaming: false
        }));
        this.finalizeStream();
        this.toast.error('Generation interrupted or failed');
      },
      complete: () => {
        this.finalizeStream();
      }
    });
  }

  public stopGeneration(): void {
    if (this.streamSub) {
      this.streamSub.unsubscribe();
      this.streamSub = undefined;
    }
    this.finalizeStream();
  }

  private finalizeStream(): void {
    this.state.updateLastAssistantMessage((msg) => ({
      ...msg,
      isStreaming: false
    }));
    this.state.isSending.set(false);
    this.state.isStreaming.set(false);
  }

  public setSearchTerm(term: string): void {
    this.state.searchTerm.set(term);
  }
}

