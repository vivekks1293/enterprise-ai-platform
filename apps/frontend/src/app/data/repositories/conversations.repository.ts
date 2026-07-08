import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiClientService } from '@data/api/api-client.service';
import { ConversationDto } from '@data/models/conversation.dto';
import { mapConversationDtoToModel } from '@data/mappers/conversation.mapper';
import { Conversation } from '@features/conversations/models/conversation.model';
import { APP_CONFIG } from '@core/tokens/app.tokens';
import { MOCK_CONVERSATIONS } from '@features/conversations/services/conversations.mock';

/**
 * Repositories are the only layer that know about DTOs and mappers.
 * Facades (and, transitively, components) only ever see domain models.
 * `enableMockData` lets the whole frontend foundation function today
 * even though the real backend/RAG API is out of scope for this sprint.
 */
@Injectable({ providedIn: 'root' })
export class ConversationsRepository {
  private readonly apiClient = inject(ApiClientService);
  private readonly config = inject(APP_CONFIG);

  public getConversations(): Observable<readonly Conversation[]> {
    if (this.config.enableMockData) {
      return of(MOCK_CONVERSATIONS);
    }

    return this.apiClient
      .get<ConversationDto[]>('conversations')
      .pipe(map((dtos) => dtos.map(mapConversationDtoToModel)));
  }
}
