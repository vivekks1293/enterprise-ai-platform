import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { HttpResponse } from '@angular/common/http';
import { KnowledgeApiService } from '@data/api-services/knowledge-api.service';
import { mapDocumentDtoToModel, mapIndexResponseDtoToModel } from '@data/mappers/document.mapper';
import { KnowledgeDocument } from '@features/documents/models/knowledge-document.model';
import { IndexResult } from '@features/documents/models/index-result.model';

/**
 * Unlike the Conversations API (which explicitly documents
 * `updated_at DESC` ordering and forbids client-side re-sorting), the
 * Knowledge API's list endpoint documents no ordering guarantee at
 * all. Sorting newest-first here is a deliberate, minor UX addition —
 * not a violation of "backend is the source of truth," since there's
 * no documented backend ordering to second-guess or disagree with.
 */
@Injectable({ providedIn: 'root' })
export class KnowledgeRepository {
  private readonly api = inject(KnowledgeApiService);

  public uploadDocument(file: File): Observable<KnowledgeDocument> {
    return this.api.upload(file).pipe(map(mapDocumentDtoToModel));
  }

  public listDocuments(): Observable<readonly KnowledgeDocument[]> {
    return this.api.list().pipe(
      map((dtos) =>
        dtos.map(mapDocumentDtoToModel).sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      )
    );
  }

  public getDocument(documentId: string): Observable<KnowledgeDocument> {
    return this.api.getById(documentId).pipe(map(mapDocumentDtoToModel));
  }

  /** Returns the full HttpResponse (headers + body) — the Facade needs
   *  the Content-Disposition header to recover the server's preferred
   *  filename before triggering the browser download. */
  public downloadDocument(documentId: string): Observable<HttpResponse<Blob>> {
    return this.api.download(documentId);
  }

  public deleteDocument(documentId: string): Observable<void> {
    return this.api.delete(documentId);
  }

  public indexDocument(documentId: string): Observable<IndexResult> {
    return this.api.index(documentId).pipe(map(mapIndexResponseDtoToModel));
  }
}
