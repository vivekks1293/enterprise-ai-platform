export type ChatMessageRole = 'user' | 'assistant';

/**
 * `status` is what lets this same shape serve both today's mock replies
 * and future token streaming: 'streaming' + empty content renders a
 * typing indicator; StreamingClientService will later update `content`
 * incrementally on the same message before flipping status to
 * 'complete' — MessageBubble's rendering logic never has to change.
 */
export type ChatMessageStatus = 'complete' | 'streaming' | 'error';

export interface ChatMessage {
  readonly id: string;
  readonly role: ChatMessageRole;
  readonly content: string;
  readonly createdAt: Date;
  readonly status: ChatMessageStatus;
}
