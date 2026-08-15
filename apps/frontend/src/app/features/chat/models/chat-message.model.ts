import { Citation } from '@features/chat/models/citation.model';

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
  /** Attached once the stream's `citations` event arrives — absent for
   *  user messages, and for assistant messages whose stream hasn't
   *  reached that event yet (or history loaded via GET conversation,
   *  which doesn't return citations — stream-only per the current
   *  backend contract). Citation UI itself is a future task; this
   *  field only exists so that future UI has state to render from. */
  readonly citations?: readonly Citation[];
}
