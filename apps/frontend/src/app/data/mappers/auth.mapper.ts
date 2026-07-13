import { LoginResponseDto, UserDto } from '@data/models/auth.dto';
import { AuthSession } from '@features/auth/models/auth-session.model';
import { User } from '@features/auth/models/user.model';

export function mapUserDtoToModel(dto: UserDto): User {
  return {
    id: dto.id,
    email: dto.email,
    displayName: dto.display_name,
    roles: dto.roles
  };
}

/**
 * `expires_in` (seconds, relative to "now") becomes `expiresAt` (an
 * absolute Date) here — the UI should never have to do that arithmetic
 * itself, and doing it once in the mapper avoids clock-drift bugs from
 * computing it again somewhere downstream.
 */
export function mapLoginResponseToAuthSession(dto: LoginResponseDto): AuthSession {
  return {
    user: mapUserDtoToModel(dto.user),
    accessToken: dto.access_token,
    expiresAt: new Date(Date.now() + dto.expires_in * 1000)
  };
}
