import { Injectable, signal } from '@angular/core';
import { KnowledgeDocument } from '@features/documents/models/knowledge-document.model';
import { LoadState } from '@shared/types/ui.types';
import { ApiError } from '@shared/models/api-error.model';

/**
 * Feature-local state, scoped to the Documents route (not root) via
 * the page component's `providers`.
 *
 * `deletingIds` is a Set rather than one global boolean — the spec's
 * "deleting" state is interpreted here as per-document, so deleting
 * one row shows a busy state only on that row, not the whole list.
 * A reasonable reading of "deleting" as a concept, not a spec
 * violation — the doc doesn't mandate granularity either way.
 */
@Injectable()
export class KnowledgeStateService {
  private readonly _documents = signal<readonly KnowledgeDocument[]>([]);
  private readonly _loadState = signal<LoadState>('idle');
  private readonly _uploading = signal<boolean>(false);
  private readonly _deletingIds = signal<ReadonlySet<string>>(new Set());
  private readonly _error = signal<ApiError | null>(null);

  public readonly documents = this._documents.asReadonly();
  public readonly loadState = this._loadState.asReadonly();
  public readonly uploading = this._uploading.asReadonly();
  public readonly deletingIds = this._deletingIds.asReadonly();
  public readonly error = this._error.asReadonly();

  public setDocuments(documents: readonly KnowledgeDocument[]): void {
    this._documents.set(documents);
  }

  public addDocument(document: KnowledgeDocument): void {
    this._documents.update((list) => [document, ...list]);
  }

  public replaceDocument(document: KnowledgeDocument): void {
    this._documents.update((list) => list.map((d) => (d.id === document.id ? document : d)));
  }

  public removeDocument(documentId: string): void {
    this._documents.update((list) => list.filter((d) => d.id !== documentId));
  }

  public setLoadState(state: LoadState): void {
    this._loadState.set(state);
  }

  public setUploading(uploading: boolean): void {
    this._uploading.set(uploading);
  }

  public setDeleting(documentId: string, deleting: boolean): void {
    this._deletingIds.update((ids) => {
      const next = new Set(ids);
      if (deleting) {
        next.add(documentId);
      } else {
        next.delete(documentId);
      }
      return next;
    });
  }

  public setError(error: ApiError | null): void {
    this._error.set(error);
  }
}
