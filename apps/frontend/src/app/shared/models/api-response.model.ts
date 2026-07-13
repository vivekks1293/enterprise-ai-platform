/**
 * Generic envelope shapes for backend responses. Not every endpoint will
 * use these — plenty of REST APIs return the raw resource — but when a
 * backend does wrap responses (e.g. `{ data, meta }`), Feature API
 * Services unwrap them here so Repositories and everything above only
 * ever see plain domain-shaped data.
 */
export interface ApiResponseMeta {
  readonly requestId?: string;
  readonly timestamp?: string;
}

export interface ApiSingleResponse<T> {
  readonly data: T;
  readonly meta?: ApiResponseMeta;
}

export interface ApiListResponse<T> {
  readonly data: readonly T[];
  readonly meta?: ApiResponseMeta & {
    readonly page?: number;
    readonly pageSize?: number;
    readonly totalCount?: number;
  };
}

/** Optional per-request retry policy — off by default, opt-in per call. */
export interface RetryPolicy {
  readonly attempts: number;
  readonly delayMs: number;
}

/** Options accepted by ApiClientService, on top of the plain URL/body. */
export interface ApiRequestOptions {
  readonly params?: Record<string, string | number | boolean>;
  readonly headers?: Record<string, string>;
  readonly retry?: RetryPolicy;
}
