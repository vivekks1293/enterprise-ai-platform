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

  /** Path is a guess (`identity/logout`, matching the confirmed
   *  `identity/login`) — not yet verified against Swagger. Confirm and
   *  update if it differs. */
  public logout(): Observable<void> {
    return this.apiClient.post<void>('identity/logout', {});
  }

  /**
   * Placeholder — not called by any component yet, and path is an
   * unconfirmed guess (`identity/me`). Confirm against Swagger before
   * wiring this up for session-restore-on-reload / silent auth.
   */
  public getCurrentUser(): Observable<UserDto> {
    return this.apiClient.get<UserDto>('identity/me');
  }

  /**
   * Placeholder — no refresh-token flow implemented yet, and path is
   * an unconfirmed guess (`identity/refresh`).
   */
  public refreshSession(): Observable<LoginResponseDto> {
    return this.apiClient.post<LoginResponseDto>('identity/refresh', {});
  }
}
