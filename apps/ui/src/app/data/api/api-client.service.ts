import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';

export interface RequestOptions {
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
}

@Injectable({ providedIn: 'root' })
export class ApiClientService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  public get<T>(path: string, options?: RequestOptions): Observable<T> {
    return this.http.get<T>(this.buildUrl(path), {
      params: this.buildParams(options?.params),
      headers: this.buildHeaders(options?.headers)
    });
  }

  public post<T>(path: string, body: unknown, options?: RequestOptions): Observable<T> {
    return this.http.post<T>(this.buildUrl(path), body, {
      params: this.buildParams(options?.params),
      headers: this.buildHeaders(options?.headers)
    });
  }

  public delete<T>(path: string, options?: RequestOptions): Observable<T> {
    return this.http.delete<T>(this.buildUrl(path), {
      params: this.buildParams(options?.params),
      headers: this.buildHeaders(options?.headers)
    });
  }

  public getBlob(path: string, options?: RequestOptions): Observable<HttpResponse<Blob>> {
    return this.http.get(this.buildUrl(path), {
      params: this.buildParams(options?.params),
      headers: this.buildHeaders(options?.headers),
      responseType: 'blob',
      observe: 'response'
    });
  }

  private buildUrl(path: string): string {
    const cleanPath = path.replace(/^\//, '');
    return `${this.baseUrl}/${cleanPath}`;
  }

  private buildParams(params?: Record<string, string | number | boolean>): HttpParams {
    let httpParams = new HttpParams();
    if (!params) return httpParams;
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== null) {
        httpParams = httpParams.set(key, String(val));
      }
    }
    return httpParams;
  }

  private buildHeaders(headers?: Record<string, string>): HttpHeaders {
    let httpHeaders = new HttpHeaders();
    if (!headers) return httpHeaders;
    for (const [key, val] of Object.entries(headers)) {
      httpHeaders = httpHeaders.set(key, val);
    }
    return httpHeaders;
  }
}

