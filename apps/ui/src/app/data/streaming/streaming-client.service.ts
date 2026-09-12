import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthSessionService } from '@core/services/auth-session.service';
import { environment } from '@env/environment';
import { SseFrameParser } from './sse-parser.util';

export interface StreamEvent<T = unknown> {
  readonly kind: 'open' | 'message' | 'done' | 'error';
  readonly event?: string;
  readonly data?: T;
  readonly error?: unknown;
}

@Injectable({ providedIn: 'root' })
export class StreamingClientService {
  private readonly session = inject(AuthSessionService);
  private readonly baseUrl = environment.streamingBaseUrl;

  public connect<T = unknown>(path: string, body: unknown): Observable<StreamEvent<T>> {
    return new Observable<StreamEvent<T>>((subscriber) => {
      const abortController = new AbortController();
      const url = `${this.baseUrl}/${path.replace(/^\//, '')}`;

      const run = async () => {
        try {
          const token = this.session.getToken();
          const response = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(body),
            signal: abortController.signal,
            headers: {
              'Content-Type': 'application/json',
              Accept: 'text/event-stream',
              ...(token ? { Authorization: `Bearer ${token}` } : {})
            }
          });

          if (!response.ok || !response.body) {
            subscriber.next({ kind: 'error', error: new Error(`HTTP ${response.status}`) });
            subscriber.error(new Error(`Stream request failed with status ${response.status}`));
            return;
          }

          subscriber.next({ kind: 'open' });

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          const parser = new SseFrameParser();

          while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            for (const frame of parser.feed(chunk)) {
              let parsedData: T;
              try {
                parsedData = JSON.parse(frame.data) as T;
              } catch {
                parsedData = frame.data as unknown as T;
              }
              subscriber.next({
                kind: 'message',
                event: frame.event,
                data: parsedData
              });
            }
          }

          subscriber.next({ kind: 'done' });
          subscriber.complete();
        } catch (err) {
          if (abortController.signal.aborted) {
            subscriber.complete();
            return;
          }
          subscriber.next({ kind: 'error', error: err });
          subscriber.error(err);
        }
      };

      run();

      return () => {
        abortController.abort();
      };
    });
  }
}

