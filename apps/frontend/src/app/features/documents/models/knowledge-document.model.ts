/**
 * Matches the real backend lifecycle: upload returns 'available'
 * immediately (there's no server-side 'uploading' status — that was
 * an earlier assumption, corrected now that the actual contract is
 * documented). Indexing is a separate, explicit step
 * (POST /documents/{id}/index) that moves a document through
 * 'indexing' → 'indexed', or 'failed' if it errors.
 */
export type DocumentStatus = 'available' | 'indexing' | 'indexed' | 'failed';

export interface KnowledgeDocument {
  readonly id: string;
  readonly filename: string;
  readonly contentType: string;
  readonly sizeBytes: number;
  readonly status: DocumentStatus;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}
