import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import { ConversationDto } from '@data/models/conversation.dto';
import { ApiListResponse } from '@shared/models/api-response.model';

/**
 * Feature API Service: knows the conversation endpoints and their DTO
 * shapes, and nothing else. No business logic (that's the Repository's
 * job), no domain models (that's the Mapper's job), no UI state (that's
 * the Facade's job). This is the layer that changes when a REST path
 * or request shape changes — everything above it is insulated.
 *
 * Every future feature gets one of these: AuthApiService,
 * DocumentApiService, SettingsApiService, etc., all following this
 * exact shape.
 */
@Injectable({ providedIn: 'root' })
export class ConversationApiService {
  private readonly apiClient = inject(ApiClientService);

  public list(page = 1, pageSize = 25): Observable<ApiListResponse<ConversationDto>> {
    return this.apiClient.get<ApiListResponse<ConversationDto>>('conversations', {
      params: { page, pageSize }
    });
  }

  public getById(id: string): Observable<ConversationDto> {
    return this.apiClient.get<ConversationDto>(`conversations/${id}`);
  }

  public delete(id: string): Observable<void> {
    return this.apiClient.delete<void>(`conversations/${id}`);
  }
}
