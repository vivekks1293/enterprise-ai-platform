import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import {
  ChatConversationDetailDto,
  ChatConversationDto,
  CreateChatConversationRequestDto
} from '@data/models/chat.dto';

/**
 * Feature API Service: knows the conversation endpoints and their DTO
 * shapes, and nothing else. Deliberately does NOT expose the
 * send-prompt endpoint — that call's *response* is a stream, not a
 * plain HTTP response, so it goes through StreamingClientService (via
 * ChatRepository) instead of ApiClientService/HttpClient. This class
 * only ever produces `Observable<T>` from a single resolved response.
 */
@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly apiClient = inject(ApiClientService);

  public createConversation(payload: CreateChatConversationRequestDto): Observable<ChatConversationDto> {
    return this.apiClient.post<ChatConversationDto>('conversations', payload);
  }

  public listConversations(): Observable<ChatConversationDto[]> {
    return this.apiClient.get<ChatConversationDto[]>('conversations');
  }

  public getConversation(conversationId: string): Observable<ChatConversationDetailDto> {
    return this.apiClient.get<ChatConversationDetailDto>(`conversations/${conversationId}`);
  }
}
