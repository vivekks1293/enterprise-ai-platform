import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import { environment } from '@env/environment';
import {
  DocumentSummaryResponse,
  UploadDocumentResponse,
  IndexDocumentResponse
} from '@data/models/document.dto';

@Injectable({ providedIn: 'root' })
export class KnowledgeApiService {
  private readonly client = inject(ApiClientService);
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  public listDocuments(): Observable<readonly DocumentSummaryResponse[]> {
    return this.client.get<readonly DocumentSummaryResponse[]>('documents');
  }

  public getDocument(id: string): Observable<DocumentSummaryResponse> {
    return this.client.get<DocumentSummaryResponse>(`documents/${id}`);
  }

  public uploadDocument(file: File): Observable<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);

    return this.http.post<UploadDocumentResponse>(`${this.baseUrl}/documents`, formData);
  }

  public indexDocument(documentId: string): Observable<IndexDocumentResponse> {
    return this.client.post<IndexDocumentResponse>(`documents/${documentId}/index`, {});
  }

  public deleteDocument(documentId: string): Observable<void> {
    return this.client.delete<void>(`documents/${documentId}`);
  }

  public downloadDocument(documentId: string): Observable<HttpResponse<Blob>> {
    return this.client.getBlob(`documents/${documentId}/download`);
  }
}

