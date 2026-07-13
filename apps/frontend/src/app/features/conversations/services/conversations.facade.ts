import { Injectable, inject } from '@angular/core';
import { ConversationsRepository } from '@data/repositories/conversations.repository';
import { ConversationsStateService } from '@features/conversations/state/conversations-state.service';
import { ApiError } from '@shared/models/api-error.model';

/**
 * Facades expose a small, component-friendly API and own the
 * orchestration between state and the data layer. Components never
 * inject the Repository, Feature API Service, or ApiClient directly
 * — only the Facade. Components also never see a raw HttpErrorResponse
 * or ApiError from a `catch` block; they only read `loadState`/`error`
 * signals that the Facade already normalized.
 */
@Injectable()
export class ConversationsFacade {
  private readonly repository = inject(ConversationsRepository);
  private readonly state = inject(ConversationsStateService);

  public readonly conversations = this.state.conversations;
  public readonly loadState = this.state.loadState;
  public readonly error = this.state.error;

  public loadConversations(): void {
    this.state.setLoadState('loading');
    this.state.setError(null);

    this.repository.getConversations().subscribe({
      next: (conversations) => {
        this.state.setConversations(conversations);
        this.state.setLoadState('success');
      },
      error: (error: ApiError) => {
        this.state.setError(error);
        this.state.setLoadState('error');
      }
    });
  }
}
