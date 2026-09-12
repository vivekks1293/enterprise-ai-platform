import { Injectable, inject } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { AuthApiService } from '@data/api-services/auth-api.service';
import { AuthSessionService } from '@core/services/auth-session.service';
import { LoginRequest, LoginResponse, UserResponse } from '@data/models/auth.dto';

@Injectable({ providedIn: 'root' })
export class AuthRepository {
  private readonly api = inject(AuthApiService);
  private readonly session = inject(AuthSessionService);

  public login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.api.login(credentials).pipe(
      tap((res) => {
        const user = {
          id: res.user?.id ?? 'current-user',
          email: res.user?.email ?? credentials.email,
          name: res.user?.name ?? credentials.email.split('@')[0],
          roleType: res.user?.role_type
        };
        this.session.setSession(user, res.access_token);
      })
    );
  }

  public getCurrentUser(): Observable<UserResponse> {
    return this.api.getCurrentUser();
  }

  public logout(): Observable<void> {
    return this.api.logout().pipe(
      tap(() => {
        this.session.clearSession();
      })
    );
  }
}

