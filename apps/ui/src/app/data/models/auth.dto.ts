export interface LoginRequest {
  readonly email: string;
  readonly password: string;
}

export interface LoginResponse {
  readonly access_token: string;
  readonly token_type: string;
  readonly user?: {
    readonly id: string;
    readonly email: string;
    readonly name: string;
    readonly role_type?: number;
  };
}

export interface UserResponse {
  readonly id: string;
  readonly email: string;
  readonly name: string;
  readonly role_type?: number;
  readonly role_type_name?: string;
}

