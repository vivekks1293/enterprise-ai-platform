export interface Conversation {
  readonly id: string;
  readonly title: string;
  readonly lastMessageAt: Date;
  readonly messageCount: number;
}
