import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { filter, map } from 'rxjs/operators';
import { ChatApiService } from '@data/api-services/chat-api.service';
import { StreamingClientService } from '@data/streaming/streaming-client.service';
import { StreamEvent } from '@data/streaming/stream-event.model';
import { mapChatConversationDtoToSummary, mapChatMessagesDto, mapSseFrameToChatStreamEvent } from '@data/mappers/chat.mapper';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { ChatStreamEvent } from '@features/chat/models/chat-stream-event.model';

export interface ChatConversationDetail {
  readonly summary: ChatConversationSummary;
  readonly messages: readonly ChatMessage[];
}

/**
 * Decides where Chat data comes from: REST for conversation
 * create/list/get, streaming for prompt submission. ChatFacade never
 * knows which transport backs a given call — it only sees domain
 * models and typed `ChatStreamEvent`s either way.
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
   * The backend now streams real Server-Sent Events
   * (`Content-Type: text/event-stream`, `event: token|citations|complete`
   * frames) rather than the earlier raw `text/plain` chunks — hence
   * `format: 'sse'` (was `format: 'text'`). `SseFrameParser`, already
   * built and unused until now, handles all the framing edge cases
   * (partial chunks, multiple frames per HTTP chunk, one frame split
   * across chunks, UTF-8 boundary safety via `TextDecoder`'s
   * `stream: true`) — nothing new needed there.
   *
   * This is also where "SSE parsing → typed stream events" resolves:
   * StreamingClientService/SseFrameParser hand back generic
   * `{ kind: 'message', event, data }` frames with no idea what a
   * "citation" is; this method turns those into typed `ChatStreamEvent`s
   * via chat.mapper.ts's `mapSseFrameToChatStreamEvent`, so ChatFacade
   * never touches a raw event name string or unparsed JSON payload.
   *
   * `filter` on `kind === 'message'` is safe with respect to errors:
   * StreamingClientService's error path calls the Observable's
   * `error()` callback directly (not just a `next()` value), so RxJS
   * propagates it through this pipe regardless of the filter/map
   * chained after it — ChatFacade's `.subscribe({ error })` still
   * fires exactly as before.
   */
  public streamPrompt(conversationId: string, prompt: string): Observable<ChatStreamEvent> {
    return this.streamingClient
      .connect<unknown>(`conversations/${conversationId}/messages`, {
        method: 'POST',
        body: { prompt },
        format: 'sse'
      })
      .pipe(
        filter((event): event is Extract<StreamEvent<unknown>, { kind: 'message' }> => event.kind === 'message'),
        map((event) => mapSseFrameToChatStreamEvent(event.event, event.data)),
        filter((event): event is ChatStreamEvent => event !== null)
      );
  }
}
