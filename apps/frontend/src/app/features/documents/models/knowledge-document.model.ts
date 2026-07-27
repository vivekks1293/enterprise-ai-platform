export type DocumentStatus = 'uploading' | 'available' | 'failed';

export interface KnowledgeDocument {
  readonly id: string;
  readonly filename: string;
  readonly contentType: string;
  readonly sizeBytes: number;
  readonly status: DocumentStatus;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}
