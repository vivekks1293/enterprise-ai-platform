/**
 * Raw wire-format DTOs for the Chat feature's backend endpoints
 * (POST/GET /conversations, GET /conversations/{id}, POST
 * /conversations/{id}/messages). Deliberately separate from
 * `conversation.dto.ts` (used by the unrelated, still-mocked
 * `features/conversations` history feature) — the two features don't
 * share a data source yet, so their DTOs shouldn't be forced together.
 */
export interface ChatConversationDto {
  readonly id: string;
  readonly title: string;
  readonly created_at: string;
  readonly updated_at: string;
}

/**
 * Backend also has SYSTEM/TOOL roles; the UI only renders USER/ASSISTANT
 * today (mapper filters the rest out) — see chat.mapper.ts.
 *
 * Casing observed from the real backend is lowercase
 * ('user'/'assistant'), while the originally documented contract used
 * uppercase ('USER'/'ASSISTANT'/'SYSTEM'/'TOOL'). Both are typed here
 * since neither is enforced at runtime — chat.mapper.ts normalizes via
 * `.toUpperCase()` before comparing, so this DTO type is documentation
 * of what's been observed, not a runtime guarantee.
 */
export type ChatMessageRoleDto = 'USER' | 'ASSISTANT' | 'SYSTEM' | 'TOOL' | 'user' | 'assistant' | 'system' | 'tool';

export interface ChatMessageDto {
  readonly id: string;
  readonly role: ChatMessageRoleDto;
  readonly content: string;
  readonly created_at: string;
}

export interface ChatConversationDetailDto extends ChatConversationDto {
  readonly messages: readonly ChatMessageDto[];
}

export interface CreateChatConversationRequestDto {
  readonly title: string;
}

export interface SendPromptRequestDto {
  readonly prompt: string;
}
