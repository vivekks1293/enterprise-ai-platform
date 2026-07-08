/**
 * Raw wire-format DTO exactly as the backend would send it. DTOs live
 * in the data layer only — they must never leak into feature
 * components. Mappers convert these into domain models.
 */
export interface ConversationDto {
  readonly id: string;
  readonly title: string;
  readonly last_message_at: string;
  readonly message_count: number;
}
