import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import { LoginRequestDto, LoginResponseDto, UserDto } from '@data/models/auth.dto';

/**
 * Feature API Service: knows the auth endpoints and their DTO shapes,
 * and nothing else. No business logic (that's AuthRepository's job),
 * no session persistence (that's Core's AuthSessionService via
 * AuthFacade), no domain models (that's auth.mapper.ts's job).
 *
 * Mirrors ConversationApiService's shape exactly — this is the second
 * proof point that the Feature API Service pattern generalizes.
 */
@Injectable({ providedIn: 'root' })
export class AuthApiService {
  private readonly apiClient = inject(ApiClientService);

  public login(payload: LoginRequestDto): Observable<LoginResponseDto> {
    return this.apiClient.post<LoginResponseDto>('identity/login', payload);
  }

  public logout(): Observable<void> {
    return this.apiClient.post<void>('auth/logout', {});
  }

  /**
   * Placeholder — not called by any component yet. Exists so
   * session-restore-on-reload and silent-authentication can call it
   * later without adding a new layer.
   */
  public getCurrentUser(): Observable<UserDto> {
    return this.apiClient.get<UserDto>('auth/me');
  }

  /**
   * Placeholder — no refresh-token flow is implemented yet, but the
   * endpoint shape is reserved so token refresh is additive later.
   */
  public refreshSession(): Observable<LoginResponseDto> {
    return this.apiClient.post<LoginResponseDto>('auth/refresh', {});
  }
}
