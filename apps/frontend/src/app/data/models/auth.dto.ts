/**
 * Raw wire-format DTOs exactly as the backend would send/expect them.
 * These never leave the data layer — mapped into domain models
 * (features/auth/models) by data/mappers/auth.mapper.ts before
 * anything else in the app sees them.
 */
export interface LoginRequestDto {
  readonly email: string;
  readonly password: string;
}

export interface UserDto {
  readonly id: string;
  readonly email: string;
  readonly name: string;
  /** Not sent by the backend yet — optional so this DTO matches the
   *  real payload today. mapUserDtoToModel() defaults it to `[]`.
   *  Once the backend adds roles, just remove the `?` here. */
  readonly roles?: readonly string[];
}

export interface LoginResponseDto {
  readonly access_token: string;
  readonly token_type: string;
  readonly expires_in: number; // seconds until expiry, from the moment of response
  readonly user: UserDto;
}
