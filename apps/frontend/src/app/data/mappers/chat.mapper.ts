import { ChatConversationDto, CitationDto, CitationsEventDto, ChatMessageDto, TokenEventDto } from '@data/models/chat.dto';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';
import { Citation } from '@features/chat/models/citation.model';
import { ChatStreamEvent } from '@features/chat/models/chat-stream-event.model';

export function mapChatConversationDtoToSummary(dto: ChatConversationDto): ChatConversationSummary {
  return {
    id: dto.id,
    title: dto.title,
    updatedAt: new Date(dto.updated_at),
    pinned: false
  };
}

/**
 * Backend messages can carry SYSTEM/TOOL roles; the UI has no
 * representation for those yet (Tool Calling / Agent Timeline are
 * explicitly out of scope this phase), so they're filtered out here
 * rather than mis-attributed to 'user' or 'assistant'. When those
 * roles need to render, this is the one place that changes.
 *
 * Role casing is normalized via `.toUpperCase()` before comparison —
 * the documented contract used UPPERCASE ('USER'/'ASSISTANT'/'SYSTEM'/
 * 'TOOL') but the deployed backend sends lowercase ('user'/'assistant').
 * Normalizing here means either casing (or a backend fix later) keeps
 * working without another round of "why are messages missing" — this
 * is the one place that assumption lives.
 */
export function mapChatMessagesDto(dtos: readonly ChatMessageDto[]): readonly ChatMessage[] {
  return dtos.filter((dto) => isRenderableRole(dto.role)).map(mapChatMessageDto);
}

function isRenderableRole(role: string): boolean {
  const normalized = role.toUpperCase();
  return normalized === 'USER' || normalized === 'ASSISTANT';
}

function mapChatMessageDto(dto: ChatMessageDto): ChatMessage {
  return {
    id: dto.id,
    role: dto.role.toUpperCase() === 'ASSISTANT' ? 'assistant' : 'user',
    content: dto.content,
    createdAt: new Date(dto.created_at),
    status: 'complete'
  };
}

export function mapCitationDtoToModel(dto: CitationDto): Citation {
  return {
    citationId: dto.citation_id,
    documentId: dto.document_id,
    chunkId: dto.chunk_id,
    filename: dto.filename,
    pageNumber: dto.page_number,
    similarityScore: dto.similarity_score
  };
}

/**
 * Turns one raw SSE frame (event name + already-JSON-parsed data) into
 * a typed `ChatStreamEvent`, or `null` for an event name this feature
 * doesn't act on. Returning `null` rather than throwing means a future
 * backend addition (e.g. `event: tool_call`) degrades gracefully —
 * ChatRepository filters `null`s out — instead of breaking the stream.
 *
 * `data` arrives as `unknown` because SseFrameParser/StreamingClientService
 * are generic and don't know Chat's payload shapes; the `as` casts here
 * are the one place that assumption is made, matching this file's
 * existing role as the sole DTO↔domain boundary for Chat.
 */
export function mapSseFrameToChatStreamEvent(eventName: string, data: unknown): ChatStreamEvent | null {
  switch (eventName) {
    case 'token': {
      const payload = data as TokenEventDto;
      return { kind: 'token', content: payload?.content ?? '' };
    }
    case 'citations': {
      const payload = data as CitationsEventDto;
      return { kind: 'citations', citations: (payload?.citations ?? []).map(mapCitationDtoToModel) };
    }
    case 'complete':
      return { kind: 'complete' };
    default:
      return null;
  }
}
