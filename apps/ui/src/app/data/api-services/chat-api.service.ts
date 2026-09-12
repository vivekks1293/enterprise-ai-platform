import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import { StreamingClientService, StreamEvent } from '@data/streaming/streaming-client.service';
import {
  ConversationSummary,
  ConversationDetailResponse,
  CreateConversationResponse
} from '@data/models/chat.dto';

@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly client = inject(ApiClientService);
  private readonly streamingClient = inject(StreamingClientService);

  public listConversations(): Observable<readonly ConversationSummary[]> {
    return this.client.get<readonly ConversationSummary[]>('conversations');
  }

  public getConversation(id: string): Observable<ConversationDetailResponse> {
    return this.client.get<ConversationDetailResponse>(`conversations/${id}`);
  }

  public createConversation(title: string): Observable<CreateConversationResponse> {
    return this.client.post<CreateConversationResponse>('conversations', { title });
  }

  public streamPrompt(conversationId: string, prompt: string): Observable<StreamEvent> {
    return this.streamingClient.connect(`conversations/${conversationId}/messages`, { prompt });
  }
}

