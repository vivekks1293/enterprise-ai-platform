import { DocumentStatus } from '@features/documents/models/knowledge-document.model';

/**
 * The index endpoint's response shape is genuinely different from
 * KnowledgeDocument (no filename/contentType/createdAt — just enough
 * to confirm the operation and report chunk_count). Kept as its own
 * small model rather than force-fit into KnowledgeDocument.
 */
export interface IndexResult {
  readonly documentId: string;
  readonly status: DocumentStatus;
  readonly chunkCount: number;
}
