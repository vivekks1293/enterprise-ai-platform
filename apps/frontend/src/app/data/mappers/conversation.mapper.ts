import { ConversationDto } from '@data/models/conversation.dto';
import { Conversation } from '@features/conversations/models/conversation.model';

/**
 * Converts wire-format DTOs into the clean domain model that
 * feature components consume. Keeping this conversion in one place
 * means a backend field rename only requires a change here.
 */
export function mapConversationDtoToModel(dto: ConversationDto): Conversation {
  return {
    id: dto.id,
    title: dto.title,
    lastMessageAt: new Date(dto.last_message_at),
    messageCount: dto.message_count
  };
}
