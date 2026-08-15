import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { APP_CONFIG } from '@core/tokens/app.tokens';
import { AuthSessionService } from '@core/services/auth-session.service';
import { LoggerService } from '@core/services/logger.service';
import { SseFrameParser } from '@data/streaming/sse-parser.util';
import { StreamEvent } from '@data/streaming/stream-event.model';
import { ApiError } from '@shared/models/api-error.model';

export interface StreamConnectOptions {
  readonly method?: 'GET' | 'POST';
  readonly body?: unknown;
  readonly headers?: Record<string, string>;
  /**
   * 'sse' (default) — `text/event-stream` framing, parsed by
   * SseFrameParser, completion signaled by a server `event: done` frame.
   * 'text' — raw plain-text transport (e.g. FastAPI's
   * `StreamingResponse(media_type="text/plain")`): no frame parsing,
   * each decoded chunk is emitted as-is, completion is detected purely
   * from the reader reaching `done: true` since plain text has no
   * explicit end-of-stream marker of its own.
   */
  readonly format?: 'sse' | 'text';
}

/**
 * The single reusable abstraction for consuming server-pushed streams.
 * This is the streaming-layer equivalent of ApiClientService: it is
 * the ONLY class in the app allowed to open a raw streaming
 * connection. Feature-specific streaming services (e.g. ChatRepository)
 * build on top of this and layer their own event-shape mapping — this
 * class knows nothing about chat, agents, or tool calls.
 *
 * Supports two wire formats via `StreamConnectOptions.format`:
 * `'sse'` (default) for `text/event-stream` framing, and `'text'` for
 * raw plain-text transports like FastAPI's
 * `StreamingResponse(media_type="text/plain")` — added in Sprint 1
 * Phase 5 once a real backend streaming endpoint existed to integrate
 * against. Existing SSE callers are unaffected; `format` defaults to
 * `'sse'`.
 *
 * This class is deliberately event-name-agnostic: every parsed SSE
 * frame is forwarded as a `{ kind: 'message', event, data }` value
 * regardless of what `event:` name the server used. Interpreting
 * specific event names (e.g. Chat's `token`/`citations`/`complete`)
 * is the caller's job — concretely, the Repository layer, which turns
 * these generic frames into feature-specific typed events. (An
 * earlier version of this class special-cased an `event: done` name
 * as an early-completion signal; that was a guess made before any
 * real backend event vocabulary existed, and was removed once Chat's
 * actual contract turned out to use `complete` instead — a good
 * reminder not to bake assumed vocabulary into a generic layer.)
 *
 * Built on `fetch` + `ReadableStream` rather than the native
 * `EventSource` API specifically because `EventSource` cannot attach
 * an `Authorization` header, which is a hard requirement for our
 * bearer-token auth model. This is the one deliberate deviation from
 * "just use the browser's SSE client" and is worth flagging in review.
 *
 * Connection lifecycle:
 *  - `connect()` returns a cold Observable<StreamEvent<T>>.
 *  - Subscribing opens the connection; unsubscribing aborts it via
 *    AbortController — this is how cancellation and automatic cleanup
 *    (e.g. a component destroyed mid-stream, or an explicit "Stop
 *    generation" action) are guaranteed.
 *  - A `{ kind: 'done' }` event is emitted and the Observable completes
 *    when the server closes the stream normally.
 *  - Any failure (network, non-2xx, malformed frame) is normalized into
 *    an ApiError and emitted as `{ kind: 'error' }`, then the Observable
 *    errors — callers use standard RxJS `catchError`/`retry`, no
 *    bespoke error channel to learn.
 *
 * Reconnection strategy is intentionally NOT implemented yet — the
 * `StreamConnectOptions` shape and the cold-Observable contract are
 * designed so a `retryWhen`-based reconnect policy can wrap `connect()`
 * later without changing this class or any of its callers.
 */
@Injectable({ providedIn: 'root' })
export class StreamingClientService {
  private readonly config = inject(APP_CONFIG);
  private readonly session = inject(AuthSessionService);
  private readonly logger = inject(LoggerService);

  public connect<TPayload = unknown>(
    path: string,
    options: StreamConnectOptions = {}
  ): Observable<StreamEvent<TPayload>> {
    return new Observable<StreamEvent<TPayload>>((subscriber) => {
      const abortController = new AbortController();
      const url = this.buildUrl(path);

      this.openConnection<TPayload>(url, options, abortController, subscriber);

      // Teardown: runs on unsubscribe, error, complete, or component
      // destruction (via takeUntilDestroyed upstream) — this is what
      // guarantees the underlying connection never leaks.
      return () => {
        abortController.abort();
      };
    });
  }

  private async openConnection<TPayload>(
    url: string,
    options: StreamConnectOptions,
    abortController: AbortController,
    subscriber: {
      next: (value: StreamEvent<TPayload>) => void;
      error: (err: ApiError) => void;
      complete: () => void;
    }
  ): Promise<void> {
    try {
      const response = await fetch(url, {
        method: options.method ?? 'GET',
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: abortController.signal,
        headers: this.buildHeaders(options.headers, options.format ?? 'sse')
      });

      if (!response.ok || !response.body) {
        subscriber.next({ kind: 'error', error: this.errorForResponse(response) });
        subscriber.error(this.errorForResponse(response));
        return;
      }

      subscriber.next({ kind: 'open' });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const format = options.format ?? 'sse';

      if (format === 'text') {
        for (;;) {
          const { value, done } = await reader.read();
          if (done) {
            break;
          }
          const chunk = decoder.decode(value, { stream: true });
          if (chunk.length > 0) {
            subscriber.next({ kind: 'message', event: 'chunk', data: chunk as unknown as TPayload });
          }
        }
        subscriber.next({ kind: 'done' });
        subscriber.complete();
        return;
      }

      const parser = new SseFrameParser();

      for (;;) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        for (const frame of parser.feed(chunk)) {
          const data = this.parseFrameData<TPayload>(frame.data);
          subscriber.next({ kind: 'message', event: frame.event, data, id: frame.id });
        }
      }

      subscriber.next({ kind: 'done' });
      subscriber.complete();
    } catch (error) {
      if (abortController.signal.aborted) {
        // Intentional cancellation (unsubscribe) — not an error condition.
        subscriber.complete();
        return;
      }
      const apiError = this.errorForException(error);
      this.logger.error(`Stream failed: ${url}`, apiError);
      subscriber.error(apiError);
    }
  }

  private buildUrl(path: string): string {
    return `${this.config.streamingBaseUrl}/${path.replace(/^\//, '')}`;
  }

  private buildHeaders(extra: Record<string, string> | undefined, format: 'sse' | 'text'): Record<string, string> {
    const token = this.session.getToken();
    return {
      Accept: format === 'text' ? 'text/plain' : 'text/event-stream',
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...extra
    };
  }

  private parseFrameData<TPayload>(raw: string): TPayload {
    try {
      return JSON.parse(raw) as TPayload;
    } catch {
      // Not every event needs to carry JSON — fall back to raw string.
      return raw as unknown as TPayload;
    }
  }

  private errorForResponse(response: Response): ApiError {
    return {
      kind: response.status >= 500 ? 'server' : 'stream',
      status: response.status,
      message: `Streaming connection failed (${response.status}).`
    };
  }

  private errorForException(error: unknown): ApiError {
    return {
      kind: 'stream',
      status: null,
      message: 'The live connection was interrupted.',
      cause: error
    };
  }
}
