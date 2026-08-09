import { DocumentDto, IndexDocumentResponseDto } from '@data/models/document.dto';
import { DocumentStatus, KnowledgeDocument } from '@features/documents/models/knowledge-document.model';
import { IndexResult } from '@features/documents/models/index-result.model';

export function mapDocumentDtoToModel(dto: DocumentDto): KnowledgeDocument {
  return {
    id: dto.id,
    filename: dto.filename,
    contentType: dto.content_type,
    sizeBytes: dto.size_bytes,
    status: normalizeStatus(dto.status),
    createdAt: new Date(dto.created_at),
    updatedAt: dto.updated_at ? new Date(dto.updated_at) : new Date(dto.created_at)
  };
}

export function mapIndexResponseDtoToModel(dto: IndexDocumentResponseDto): IndexResult {
  return {
    documentId: dto.document_id,
    status: normalizeStatus(dto.status),
    chunkCount: dto.chunk_count
  };
}

/**
 * Normalizes case defensively (see the DTO's status field comment)
 * and fails safe: an unrecognized status maps to 'failed' rather than
 * 'available'/'indexed', so the UI never implies a document is in a
 * better state than we can actually confirm from what the backend sent.
 */
function normalizeStatus(raw: string): DocumentStatus {
  const normalized = raw.toLowerCase();
  if (normalized === 'available' || normalized === 'indexing' || normalized === 'indexed' || normalized === 'failed') {
    return normalized;
  }
  return 'failed';
}
