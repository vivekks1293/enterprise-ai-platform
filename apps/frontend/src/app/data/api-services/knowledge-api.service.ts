import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import { DocumentDto } from '@data/models/document.dto';

/**
 * Feature API Service: knows the document endpoints, their DTO
 * shapes, and the multipart/blob request mechanics — nothing else.
 * The backend derives ownership entirely from the JWT (already
 * attached by authInterceptor on every request via ApiClientService);
 * this class never sends owner_id/user_id, and never will.
 */
@Injectable({ providedIn: 'root' })
export class KnowledgeApiService {
  private readonly apiClient = inject(ApiClientService);

  /**
   * `FormData` as the body is enough — ApiClientService never force-sets
   * Content-Type, so the browser generates the correct multipart
   * boundary automatically. Explicitly NOT setting a Content-Type
   * header here is load-bearing, not an oversight.
   */
  public upload(file: File): Observable<DocumentDto> {
    const formData = new FormData();
    formData.append('file', file);
    return this.apiClient.post<DocumentDto>('documents', formData);
  }

  public list(): Observable<DocumentDto[]> {
    return this.apiClient.get<DocumentDto[]>('documents');
  }

  public getById(documentId: string): Observable<DocumentDto> {
    return this.apiClient.get<DocumentDto>(`documents/${documentId}`);
  }

  public download(documentId: string): Observable<Blob> {
    return this.apiClient.getBlob(`documents/${documentId}/download`);
  }

  /** 204 No Content on success — nothing to parse, `void` is correct. */
  public delete(documentId: string): Observable<void> {
    return this.apiClient.delete<void>(`documents/${documentId}`);
  }
}
