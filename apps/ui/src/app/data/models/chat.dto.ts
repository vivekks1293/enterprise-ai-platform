export interface Citation {
  readonly citationId?: string;
  readonly documentId: string;
  readonly chunkId: string;
  readonly filename: string;
  readonly pageNumber?: number | null;
  readonly similarityScore: number;
  readonly contentSnippet?: string;
}

export interface ChatMessage {
  readonly id: string;
  readonly role: 'user' | 'assistant' | 'system';
  readonly content: string;
  readonly createdAt: string;
  readonly citations?: readonly Citation[];
  readonly isStreaming?: boolean;
}

export interface ConversationSummary {
  readonly id: string;
  readonly title: string;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface ConversationDetailResponse {
  readonly id: string;
  readonly title: string;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly messages: readonly {
    readonly id: string;
    readonly role: string;
    readonly content: string;
    readonly created_at?: string;
    readonly createdAt?: string;
  }[];
}

export interface CreateConversationResponse {
  readonly id: string;
  readonly title: string;
  readonly created_at: string;
  readonly updated_at: string;
}

export type AIStreamEventType = 'token' | 'citations' | 'complete' | 'error';

export interface AIStreamEvent {
  readonly type: AIStreamEventType;
  readonly content?: string;
  readonly citations?: readonly Citation[];
}

