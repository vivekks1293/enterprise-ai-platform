import { Injectable, computed, inject } from '@angular/core';
import { KnowledgeStateService } from '@features/documents/state/knowledge-state.service';
import { KnowledgeRepository } from '@data/repositories/knowledge.repository';
import { KnowledgeDocument } from '@features/documents/models/knowledge-document.model';
import { triggerBlobDownload } from '@core/utils/file-download.util';
import { ApiError } from '@shared/models/api-error.model';

/**
 * The only thing DocumentsPageComponent is allowed to inject.
 *
 * Every method here is a plain REST call (no streaming, unlike Chat),
 * which means every failure already goes through ApiClientService →
 * HttpClient → error.interceptor.ts and gets normalized + toasted
 * automatically. This Facade never calls NotificationService itself —
 * it only updates its own loading/error signals, exactly like
 * ChatFacade's REST methods (create/list/get conversation).
 */
@Injectable()
export class KnowledgeFacade {
  private readonly state = inject(KnowledgeStateService);
  private readonly repository = inject(KnowledgeRepository);

  public readonly documents = this.state.documents;
  public readonly loadState = this.state.loadState;
  public readonly uploading = this.state.uploading;
  public readonly error = this.state.error;

  private readonly deletingIds = this.state.deletingIds;

  public isDeleting(documentId: string): boolean {
    return this.deletingIds().has(documentId);
  }

  public readonly hasDocuments = computed(() => this.state.documents().length > 0);

  public loadDocuments(): void {
    this.state.setLoadState('loading');
    this.repository.listDocuments().subscribe({
      next: (documents) => {
        this.state.setDocuments(documents);
        this.state.setLoadState('success');
      },
      error: (error: ApiError) => {
        // Already toasted by error.interceptor.ts — just reflect state here.
        this.state.setError(error);
        this.state.setLoadState('error');
      }
    });
  }

  /** Prepends the uploaded document straight from the 201 response —
   *  matches ConversationsFacade/ChatFacade's existing "add to local
   *  state" pattern rather than reloading the whole list. */
  public uploadDocument(file: File): void {
    this.state.setUploading(true);
    this.state.setError(null);

    this.repository.uploadDocument(file).subscribe({
      next: (document) => {
        this.state.addDocument(document);
        this.state.setUploading(false);
      },
      error: (error: ApiError) => {
        // Already toasted by error.interceptor.ts — just reflect state here.
        this.state.setError(error);
        this.state.setUploading(false);
      }
    });
  }

  /** Refreshes a single document's metadata in place — e.g. useful
   *  later for polling a document stuck in 'uploading' status until
   *  it flips to 'available'/'failed'. Not wired to any polling loop
   *  yet; exposed now so that future addition doesn't need a new
   *  Facade method. */
  public refreshDocument(documentId: string): void {
    this.repository.getDocument(documentId).subscribe({
      next: (document) => this.state.replaceDocument(document),
      error: (error: ApiError) => this.state.setError(error)
    });
  }

  public downloadDocument(document: KnowledgeDocument): void {
    this.repository.downloadDocument(document.id).subscribe({
      next: (blob) => triggerBlobDownload(blob, document.filename),
      error: (error: ApiError) => this.state.setError(error)
    });
  }

  public deleteDocument(documentId: string): void {
    this.state.setDeleting(documentId, true);
    this.repository.deleteDocument(documentId).subscribe({
      next: () => {
        this.state.removeDocument(documentId);
        this.state.setDeleting(documentId, false);
      },
      error: (error: ApiError) => {
        // Already toasted by error.interceptor.ts — just reflect state here.
        this.state.setError(error);
        this.state.setDeleting(documentId, false);
      }
    });
  }
}
