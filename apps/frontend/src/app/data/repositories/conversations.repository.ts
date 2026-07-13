import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { ConversationApiService } from '@data/api-services/conversation-api.service';
import { mapConversationDtoToModel } from '@data/mappers/conversation.mapper';
import { Conversation } from '@features/conversations/models/conversation.model';
import { APP_CONFIG } from '@core/tokens/app.tokens';
import { MOCK_CONVERSATIONS } from '@features/conversations/services/conversations.mock';

/**
 * Repositories decide WHERE data comes from and own that decision
 * exclusively — Facades never know whether a given call hit REST,
 * a cache, or (as today) an in-memory mock. This is what lets the
 * data source evolve — REST today, IndexedDB/offline cache tomorrow —
 * without the Repository's public method signatures ever changing.
 *
 * Only the Repository knows about DTOs and Mappers; everything above
 * it (Facade, Component) only ever sees the `Conversation` domain model.
 *
 * `enableMockData` lets the whole frontend foundation function today
 * even though the real backend/RAG API is out of scope for this sprint.
 * Flipping that flag off is the only change needed once the backend
 * conversations endpoint exists — nothing else in this class changes.
 */
@Injectable({ providedIn: 'root' })
export class ConversationsRepository {
  private readonly conversationApi = inject(ConversationApiService);
  private readonly config = inject(APP_CONFIG);

  public getConversations(): Observable<readonly Conversation[]> {
    if (this.config.enableMockData) {
      return of(MOCK_CONVERSATIONS);
    }

    return this.conversationApi
      .list()
      .pipe(map((response) => response.data.map(mapConversationDtoToModel)));
  }

  public getConversationById(id: string): Observable<Conversation> {
    if (this.config.enableMockData) {
      const found = MOCK_CONVERSATIONS.find((conversation) => conversation.id === id);
      if (!found) {
        throw new Error(`Mock conversation not found: ${id}`);
      }
      return of(found);
    }

    return this.conversationApi.getById(id).pipe(map(mapConversationDtoToModel));
  }

  public deleteConversation(id: string): Observable<void> {
    if (this.config.enableMockData) {
      return of(undefined);
    }

    return this.conversationApi.delete(id);
  }
}
