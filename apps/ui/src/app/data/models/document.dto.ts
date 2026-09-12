export type DocumentStatus = 'available' | 'indexing' | 'indexed' | 'failed' | 'uploading';

export interface KnowledgeDocument {
  readonly id: string;
  readonly filename: string;
  readonly contentType: string;
  readonly sizeBytes: number;
  readonly status: DocumentStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface DocumentSummaryResponse {
  readonly id: string;
  readonly filename: string;
  readonly content_type: string;
  readonly size_bytes: number;
  readonly status: string;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface UploadDocumentResponse {
  readonly id: string;
  readonly filename: string;
  readonly content_type: string;
  readonly size_bytes: number;
  readonly status: string;
  readonly created_at: string;
}

export interface IndexDocumentResponse {
  readonly document_id: string;
  readonly status: string;
  readonly chunk_count?: number;
}

