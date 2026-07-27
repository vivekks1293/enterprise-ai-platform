import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { retry as retryOperator } from 'rxjs/operators';
import { APP_CONFIG } from '@core/tokens/app.tokens';
import { ApiRequestOptions, RetryPolicy } from '@shared/models/api-response.model';

/**
 * The ONLY place in the app that is allowed to call HttpClient
 * directly. Every Feature API Service depends on this instead of
 * injecting HttpClient itself, so base URL, headers, retry policy,
 * and future concerns (request signing, tracing) are handled in
 * exactly one spot.
 *
 * Flow: Component → Facade → Repository → Feature API Service → ApiClient → Backend
 *
 * Error normalization happens in `error.interceptor.ts`, not here —
 * this class stays a thin, generic HTTP wrapper so it has no opinion
 * about what a normalized error looks like.
 */
@Injectable({ providedIn: 'root' })
export class ApiClientService {
  private readonly http = inject(HttpClient);
  private readonly config = inject(APP_CONFIG);

  public get<T>(path: string, options?: ApiRequestOptions): Observable<T> {
    return this.withRetry(
      this.http.get<T>(this.buildUrl(path), {
        params: this.buildParams(options?.params),
        headers: this.buildHeaders(options?.headers)
      }),
      options?.retry
    );
  }

  /**
   * For endpoints that return a raw file (not JSON) — e.g. document
   * download. Angular's `responseType: 'blob'` skips JSON parsing
   * entirely. Known caveat: if the server returns a non-2xx status
   * with a JSON error body, Angular may still deliver that error body
   * as a Blob rather than parsed JSON (a long-standing HttpClient
   * quirk with binary responseTypes), so `api-error.util.ts`'s
   * `extractBackendMessage` can fail to read the backend's specific
   * message for a failed blob request — it falls back to a generic
   * per-status message instead, which is still safe, just less
   * specific. Not worth a bespoke error-parsing path for one endpoint
   * this early — flagged here for whoever hits it next.
   */
  public getBlob(path: string, options?: ApiRequestOptions): Observable<Blob> {
    return this.http.get(this.buildUrl(path), {
      params: this.buildParams(options?.params),
      headers: this.buildHeaders(options?.headers),
      responseType: 'blob'
    });
  }

  public post<T>(path: string, body: unknown, options?: ApiRequestOptions): Observable<T> {
    return this.withRetry(
      this.http.post<T>(this.buildUrl(path), body, {
        params: this.buildParams(options?.params),
        headers: this.buildHeaders(options?.headers)
      }),
      options?.retry
    );
  }

  public put<T>(path: string, body: unknown, options?: ApiRequestOptions): Observable<T> {
    return this.withRetry(
      this.http.put<T>(this.buildUrl(path), body, {
        params: this.buildParams(options?.params),
        headers: this.buildHeaders(options?.headers)
      }),
      options?.retry
    );
  }

  public patch<T>(path: string, body: unknown, options?: ApiRequestOptions): Observable<T> {
    return this.withRetry(
      this.http.patch<T>(this.buildUrl(path), body, {
        params: this.buildParams(options?.params),
        headers: this.buildHeaders(options?.headers)
      }),
      options?.retry
    );
  }

  public delete<T>(path: string, options?: ApiRequestOptions): Observable<T> {
    return this.withRetry(
      this.http.delete<T>(this.buildUrl(path), {
        params: this.buildParams(options?.params),
        headers: this.buildHeaders(options?.headers)
      }),
      options?.retry
    );
  }

  private buildUrl(path: string): string {
    return `${this.config.apiBaseUrl}/${path.replace(/^\//, '')}`;
  }

  private buildParams(params?: Record<string, string | number | boolean>): HttpParams {
    let httpParams = new HttpParams();
    if (!params) {
      return httpParams;
    }
    for (const [key, value] of Object.entries(params)) {
      httpParams = httpParams.set(key, String(value));
    }
    return httpParams;
  }

  private buildHeaders(headers?: Record<string, string>): HttpHeaders {
    return headers ? new HttpHeaders(headers) : new HttpHeaders();
  }

  /** No retry unless a caller explicitly opts in via `options.retry` — retrying
   *  by default risks duplicating non-idempotent requests (e.g. POST). */
  private withRetry<T>(source: Observable<T>, policy?: RetryPolicy): Observable<T> {
    if (!policy) {
      return source;
    }
    return source.pipe(retryOperator({ count: policy.attempts, delay: policy.delayMs }));
  }
}
