import { ChatConversationDto, ChatMessageDto } from '@data/models/chat.dto';
import { ChatConversationSummary } from '@features/chat/models/chat-conversation-summary.model';
import { ChatMessage } from '@features/chat/models/chat-message.model';

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
