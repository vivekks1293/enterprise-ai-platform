import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ChatApiService } from '@data/api-services/chat-api.service';
import {
  ChatMessage,
  ConversationSummary,
  ConversationDetailResponse,
  CreateConversationResponse,
  AIStreamEvent
} from '@data/models/chat.dto';

@Injectable({ providedIn: 'root' })
export class ChatRepository {
  private readonly api = inject(ChatApiService);

  public listConversations(): Observable<readonly ConversationSummary[]> {
    return this.api.listConversations().pipe(
      map((items) =>
        items.map((item) => ({
          id: item.id,
          title: item.title,
          createdAt: item.createdAt ?? (item as any).created_at,
          updatedAt: item.updatedAt ?? (item as any).updated_at
        }))
      )
    );
  }

  public getConversation(id: string): Observable<{ title: string; messages: readonly ChatMessage[] }> {
    return this.api.getConversation(id).pipe(
      map((res: ConversationDetailResponse) => ({
        title: res.title,
        messages: res.messages.map((m) => ({
          id: m.id,
          role: m.role as 'user' | 'assistant' | 'system',
          content: m.content,
          createdAt: m.createdAt ?? m.created_at ?? new Date().toISOString()
        }))
      }))
    );
  }

  public createConversation(title: string): Observable<CreateConversationResponse> {
    return this.api.createConversation(title);
  }

  public streamPrompt(conversationId: string, prompt: string): Observable<AIStreamEvent> {
    return this.api.streamPrompt(conversationId, prompt).pipe(
      map((streamEvent) => {
        if (streamEvent.kind === 'error') {
          return { type: 'error' } as AIStreamEvent;
        }
        if (streamEvent.kind === 'done') {
          return { type: 'complete' } as AIStreamEvent;
        }
        if (streamEvent.kind === 'message') {
          const rawEvent = streamEvent.event;
          const data = streamEvent.data as any;

          if (rawEvent === 'token') {
            return {
              type: 'token',
              content: data?.content ?? ''
            };
          }
          if (rawEvent === 'citations') {
            return {
              type: 'citations',
              citations: (data?.citations ?? []).map((c: any) => ({
                citationId: c.citation_id,
                documentId: c.document_id,
                chunkId: c.chunk_id,
                filename: c.filename,
                pageNumber: c.page_number,
                similarityScore: c.similarity_score,
                contentSnippet: c.content_snippet
              }))
            };
          }
          if (rawEvent === 'complete') {
            return { type: 'complete' };
          }
        }
        return { type: 'complete' } as AIStreamEvent;
      })
    );
  }
}

