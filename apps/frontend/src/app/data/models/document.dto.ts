/**
 * Raw wire-format DTOs for the Knowledge (Document Management) API.
 * Upload responses omit `updated_at` per the documented contract;
 * list/detail responses include it — modeled as one shared DTO with
 * `updated_at` optional rather than two near-duplicate interfaces,
 * since every other field is identical across all three endpoints.
 */
export interface DocumentDto {
  readonly id: string;
  readonly filename: string;
  readonly content_type: string;
  readonly size_bytes: number;
  /** Documented values: 'available' | 'uploading' | 'failed' — kept as
   *  a plain string here (not a literal union) since we already got
   *  burned once by assuming exact backend casing (see chat.dto.ts's
   *  role-casing note). Normalization happens in document.mapper.ts. */
  readonly status: string;
  readonly created_at: string;
  readonly updated_at?: string;
}
