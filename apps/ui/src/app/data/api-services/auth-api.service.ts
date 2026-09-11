import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClientService } from '@data/api/api-client.service';
import { LoginRequest, LoginResponse, UserResponse } from '@data/models/auth.dto';

@Injectable({ providedIn: 'root' })
export class AuthApiService {
  private readonly client = inject(ApiClientService);

  public login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.client.post<LoginResponse>('identity/login', credentials);
  }

  public getCurrentUser(): Observable<UserResponse> {
    return this.client.get<UserResponse>('identity/me');
  }

  public logout(): Observable<void> {
    return this.client.post<void>('identity/logout', {});
  }
}

