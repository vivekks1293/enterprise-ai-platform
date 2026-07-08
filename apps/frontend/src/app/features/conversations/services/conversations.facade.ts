import { Injectable, inject } from '@angular/core';
import { finalize } from 'rxjs';
import { ConversationsRepository } from '@data/repositories/conversations.repository';
import { ConversationsStateService } from '@features/conversations/state/conversations-state.service';

/**
 * Facades expose a small, component-friendly API and own the
 * orchestration between state and the data layer. Components never
 * inject the Repository or ApiClient directly — only the Facade.
 */
@Injectable()
export class ConversationsFacade {
  private readonly repository = inject(ConversationsRepository);
  private readonly state = inject(ConversationsStateService);

  public readonly conversations = this.state.conversations;
  public readonly loadState = this.state.loadState;

  public loadConversations(): void {
    this.state.setLoadState('loading');
    this.repository
      .getConversations()
      .pipe(finalize(() => this.state.setLoadState('success')))
      .subscribe({
        next: (conversations) => this.state.setConversations(conversations),
        error: () => this.state.setLoadState('error')
      });
  }
}
