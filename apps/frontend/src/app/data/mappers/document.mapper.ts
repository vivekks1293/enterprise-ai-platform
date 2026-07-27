import { DocumentDto } from '@data/models/document.dto';
import { DocumentStatus, KnowledgeDocument } from '@features/documents/models/knowledge-document.model';

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

/**
 * Normalizes case defensively (see the DTO's status field comment)
 * and fails safe: an unrecognized status maps to 'failed' rather than
 * 'available', so the UI never implies a document is usable/downloadable
 * when we can't actually confirm that from what the backend sent.
 */
function normalizeStatus(raw: string): DocumentStatus {
  const normalized = raw.toLowerCase();
  if (normalized === 'available' || normalized === 'uploading' || normalized === 'failed') {
    return normalized;
  }
  return 'failed';
}
