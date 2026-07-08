import { Injectable, signal } from '@angular/core';
import { Conversation } from '@features/conversations/models/conversation.model';
import { LoadState } from '@shared/types/ui.types';

/**
 * Feature-local state. Not provided in root — scoped to the
 * `conversations` feature via its route providers, so it resets
 * cleanly if the feature is lazy-loaded/unloaded.
 */
@Injectable()
export class ConversationsStateService {
  private readonly _conversations = signal<readonly Conversation[]>([]);
  private readonly _loadState = signal<LoadState>('idle');

  public readonly conversations = this._conversations.asReadonly();
  public readonly loadState = this._loadState.asReadonly();

  public setConversations(conversations: readonly Conversation[]): void {
    this._conversations.set(conversations);
  }

  public setLoadState(state: LoadState): void {
    this._loadState.set(state);
  }
}
