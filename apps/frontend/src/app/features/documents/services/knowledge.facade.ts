import { Injectable, computed, inject } from '@angular/core';
import { KnowledgeStateService } from '@features/documents/state/knowledge-state.service';
import { KnowledgeRepository } from '@data/repositories/knowledge.repository';
import { KnowledgeDocument } from '@features/documents/models/knowledge-document.model';
import { extractFilenameFromContentDisposition, triggerBlobDownload } from '@core/utils/file-download.util';
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
   *  later for polling a document stuck in 'indexing' status until it
   *  flips to 'indexed'/'failed'. Not wired to any polling loop yet;
   *  exposed now so that future addition doesn't need a new Facade
   *  method. */
  public refreshDocument(documentId: string): void {
    this.repository.getDocument(documentId).subscribe({
      next: (document) => this.state.replaceDocument(document),
      error: (error: ApiError) => this.state.setError(error)
    });
  }

  /**
   * Uses the filename from Content-Disposition when the backend sends
   * one, falling back to the document's already-known filename
   * otherwise — matches the documented contract ("download the file
   * using the filename from the Content-Disposition header if present").
   */
  public downloadDocument(document: KnowledgeDocument): void {
    this.repository.downloadDocument(document.id).subscribe({
      next: (response) => {
        const blob = response.body;
        if (!blob) {
          return;
        }
        const filename =
          extractFilenameFromContentDisposition(response.headers.get('Content-Disposition')) ?? document.filename;
        triggerBlobDownload(blob, filename);
      },
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

  public isIndexing(documentId: string): boolean {
    return this.state.indexingIds().has(documentId);
  }

  /**
   * Per the documented flow, a successful index refreshes the whole
   * document list rather than patching this one row in place. That's
   * implemented via `refreshDocumentsSilently()` below, NOT
   * `loadDocuments()` — reusing `loadDocuments()` here would toggle
   * the page-level `loadState` to 'loading', swapping the entire table
   * out for a full-page spinner on every Index click, which reads as a
   * bug (a jarring flash) rather than a background refresh. The list
   * genuinely does refresh either way; this just avoids an unintended
   * side effect of literal method reuse.
   */
  public indexDocument(documentId: string): void {
    this.state.setIndexing(documentId, true);
    this.repository.indexDocument(documentId).subscribe({
      next: () => {
        this.state.setIndexing(documentId, false);
        this.refreshDocumentsSilently();
      },
      error: (error: ApiError) => {
        // Already toasted by error.interceptor.ts — just reflect state here.
        this.state.setError(error);
        this.state.setIndexing(documentId, false);
      }
    });
  }

  /** Background refresh that doesn't disturb the page-level loadState —
   *  see indexDocument()'s doc comment for why this exists separately
   *  from loadDocuments(). */
  private refreshDocumentsSilently(): void {
    this.repository.listDocuments().subscribe({
      next: (documents) => this.state.setDocuments(documents),
      error: (error: ApiError) => this.state.setError(error)
    });
  }
}
