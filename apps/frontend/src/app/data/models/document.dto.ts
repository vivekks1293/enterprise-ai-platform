/**
 * Raw wire-format DTOs for the Knowledge (Document Management) API.
 * `updated_at` is optional since none of the documented response
 * examples (upload/list/get) actually include it — the mapper falls
 * back to `created_at` when absent.
 */
export interface DocumentDto {
  readonly id: string;
  readonly filename: string;
  readonly content_type: string;
  readonly size_bytes: number;
  /** Documented values: 'available' | 'indexing' | 'indexed' | 'failed'
   *  — kept as a plain string here (not a literal union) since we
   *  already got burned once by assuming exact backend casing (see
   *  chat.dto.ts's role-casing note). Normalization happens in
   *  document.mapper.ts. */
  readonly status: string;
  readonly created_at: string;
  readonly updated_at?: string;
}

/** Response shape for POST /documents/{id}/index — deliberately
 *  different from DocumentDto (uses `document_id`, not `id`, and has
 *  no filename/content_type/created_at at all). */
export interface IndexDocumentResponseDto {
  readonly document_id: string;
  readonly status: string;
  readonly chunk_count: number;
}
