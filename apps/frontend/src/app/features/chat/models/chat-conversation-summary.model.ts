/**
 * Sidebar list item for the Chat workspace. Deliberately NOT the same
 * model as `features/conversations/models/conversation.model.ts` — see
 * the architecture note in Phase 4's explanation for why forcing
 * these two to share a shape now would be premature coupling.
 */
export interface ChatConversationSummary {
  readonly id: string;
  readonly title: string;
  /** The backend doesn't return a last-message snippet yet — reserved
   *  for if/when it does. `ConversationItemComponent` falls back to
   *  generic text when this is absent. */
  readonly preview?: string;
  readonly updatedAt: Date;
  /** The backend has no pinning concept yet — always `false` for
   *  backend-sourced conversations. Kept so the Pinned/Recent sidebar
   *  split (built in Phase 4) needs no changes if pinning is added later. */
  readonly pinned: boolean;
}
