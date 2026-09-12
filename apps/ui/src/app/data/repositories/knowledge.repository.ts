import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { HttpResponse } from '@angular/common/http';
import { KnowledgeApiService } from '@data/api-services/knowledge-api.service';
import {
  KnowledgeDocument,
  DocumentStatus,
  UploadDocumentResponse,
  IndexDocumentResponse
} from '@data/models/document.dto';

@Injectable({ providedIn: 'root' })
export class KnowledgeRepository {
  private readonly api = inject(KnowledgeApiService);

  public listDocuments(): Observable<readonly KnowledgeDocument[]> {
    return this.api.listDocuments().pipe(
      map((items) =>
        items.map((item) => ({
          id: item.id,
          filename: item.filename,
          contentType: item.content_type,
          sizeBytes: item.size_bytes,
          status: (item.status?.toLowerCase() || 'available') as DocumentStatus,
          createdAt: item.created_at,
          updatedAt: item.updated_at
        }))
      )
    );
  }

  public uploadDocument(file: File): Observable<KnowledgeDocument> {
    return this.api.uploadDocument(file).pipe(
      map((res: UploadDocumentResponse) => ({
        id: res.id,
        filename: res.filename,
        contentType: res.content_type,
        sizeBytes: res.size_bytes,
        status: (res.status?.toLowerCase() || 'indexed') as DocumentStatus,
        createdAt: res.created_at,
        updatedAt: res.created_at
      }))
    );
  }

  public indexDocument(id: string): Observable<IndexDocumentResponse> {
    return this.api.indexDocument(id);
  }

  public deleteDocument(id: string): Observable<void> {
    return this.api.deleteDocument(id);
  }

  public downloadDocument(id: string): Observable<HttpResponse<Blob>> {
    return this.api.downloadDocument(id);
  }
}

