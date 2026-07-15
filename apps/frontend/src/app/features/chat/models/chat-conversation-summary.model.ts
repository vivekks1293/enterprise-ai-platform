/**
 * Sidebar list item for the Chat workspace. Deliberately NOT the same
 * model as `features/conversations/models/conversation.model.ts` — see
 * the architecture note in this phase's explanation for why forcing
 * these two to share a shape now would be premature coupling.
 */
export interface ChatConversationSummary {
  readonly id: string;
  readonly title: string;
  readonly preview: string;
  readonly updatedAt: Date;
  readonly pinned: boolean;
}
