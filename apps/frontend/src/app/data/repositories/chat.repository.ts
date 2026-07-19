import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ChatApiService } from '@data/api-services/chat-api.service';
import { StreamingClientService } from '@data/streaming/streaming-client.service';
import { StreamEvent } from '@data/streaming/stream-event.model';
import { mapChatConversationDtoToSummary, mapChatMessagesDto } from '@data/mappers/chat.mapper';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';

export interface ChatConversationDetail {
  readonly summary: ChatConversationSummary;
  readonly messages: readonly ChatMessage[];
}

/**
 * Decides where Chat data comes from: REST for conversation
 * create/list/get, streaming for prompt submission. ChatFacade never
 * knows which transport backs a given call — it only sees domain
 * models and StreamEvent<string> chunks either way.
 *
 * No client-side sorting of `listConversations()` results — the
 * backend already returns `updated_at DESC` and is the source of
 * truth for ordering.
 */
@Injectable({ providedIn: 'root' })
export class ChatRepository {
  private readonly chatApi = inject(ChatApiService);
  private readonly streamingClient = inject(StreamingClientService);

  public createConversation(title: string): Observable<ChatConversationSummary> {
    return this.chatApi.createConversation({ title }).pipe(map(mapChatConversationDtoToSummary));
  }

  public listConversations(): Observable<readonly ChatConversationSummary[]> {
    return this.chatApi.listConversations().pipe(map((dtos) => dtos.map(mapChatConversationDtoToSummary)));
  }

  public getConversation(conversationId: string): Observable<ChatConversationDetail> {
    return this.chatApi.getConversation(conversationId).pipe(
      map((dto) => ({
        summary: mapChatConversationDtoToSummary(dto),
        messages: mapChatMessagesDto(dto.messages)
      }))
    );
  }

  /**
   * Backend streams `text/plain` chunks (FastAPI's
   * `StreamingResponse`), not Server-Sent Events — `format: 'text'`
   * tells StreamingClientService to skip SSE frame parsing and emit
   * each decoded chunk directly. Each emitted `StreamEvent.data` is a
   * raw string fragment; ChatFacade appends it to the in-flight
   * assistant message's content.
   */
  public streamPrompt(conversationId: string, prompt: string): Observable<StreamEvent<string>> {
    return this.streamingClient.connect<string>(`conversations/${conversationId}/messages`, {
      method: 'POST',
      body: { prompt },
      format: 'text'
    });
  }
}
