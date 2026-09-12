import { Injectable, inject } from '@angular/core';
import { Observable, map, filter } from 'rxjs';
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
      map((raw: any) => {
        const items: any[] = Array.isArray(raw) ? raw : (raw?.conversations ?? raw?.data ?? []);
        return items.map((item: any) => ({
          id: String(item.id),
          title: item.title || 'Untitled Conversation',
          createdAt: item.createdAt ?? item.created_at ?? new Date().toISOString(),
          updatedAt: item.updatedAt ?? item.updated_at ?? new Date().toISOString()
        }));
      })
    );
  }

  public getConversation(id: string): Observable<{ title: string; messages: readonly ChatMessage[] }> {
    return this.api.getConversation(id).pipe(
      map((res: any) => {
        const rawMessages: any[] = Array.isArray(res?.messages) ? res.messages : [];
        return {
          title: res?.title || 'Conversation',
          messages: rawMessages.map((m: any) => ({
            id: String(m.id),
            role: (m.role || 'assistant') as 'user' | 'assistant' | 'system',
            content: m.content || '',
            createdAt: m.createdAt ?? m.created_at ?? new Date().toISOString()
          }))
        };
      })
    );
  }

  public createConversation(title: string): Observable<CreateConversationResponse> {
    return this.api.createConversation(title);
  }

  public streamPrompt(conversationId: string, prompt: string): Observable<AIStreamEvent> {
    return this.api.streamPrompt(conversationId, prompt).pipe(
      filter((streamEvent) => streamEvent.kind !== 'open'),
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
            return { type: 'complete' } as AIStreamEvent;
          }
        }
        return null;
      }),
      filter((e): e is AIStreamEvent => e !== null)
    );
  }
}

