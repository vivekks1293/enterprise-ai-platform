import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AvatarComponent } from '@shared/ui/avatar/avatar.component';
import { ClickOutsideDirective } from '@shared/directives/click-outside.directive';
import { AuthSessionService } from '@core/services/auth-session.service';
import { ROUTE_PATHS } from '@core/constants/app.constants';

/**
 * Reads the current user from Core's AuthSessionService — allowed,
 * since Core is foundational, not a feature. "Sign out" is a
 * `routerLink` to `/auth/logout` rather than a call into
 * `AuthFacade` — Shell references a URL string, exactly like
 * `authGuard` does, and never imports anything from `features/auth`.
 * This is what keeps Shell independent of business features true even
 * though it needs a working sign-out control.
 */
@Component({
  selector: 'eap-user-menu',
  standalone: true,
  imports: [CommonModule, RouterModule, AvatarComponent, ClickOutsideDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-user-menu" (eapClickOutside)="close()">
      <button
        type="button"
        class="eap-user-menu__trigger"
        (click)="toggle()"
        aria-haspopup="true"
        [attr.aria-expanded]="isOpen()"
      >
        <eap-avatar [name]="session.currentUser()?.displayName ?? ''" size="sm"></eap-avatar>
      </button>
      @if (isOpen()) {
        <div class="eap-user-menu__dropdown" role="menu">
          @if (session.currentUser(); as user) {
            <div class="eap-user-menu__identity">
              <div class="eap-user-menu__name">{{ user.displayName }}</div>
              <div class="eap-user-menu__email">{{ user.email }}</div>
            </div>
          }
          <a class="eap-user-menu__item" role="menuitem" [routerLink]="profilePath">Profile</a>
          <a class="eap-user-menu__item" role="menuitem" [routerLink]="settingsPath">Settings</a>
          <a class="eap-user-menu__item eap-user-menu__item--danger" role="menuitem" [routerLink]="logoutPath">
            Sign out
          </a>
        </div>
      }
    </div>
  `,
  styles: `
    .eap-user-menu {
      position: relative;
    }
    .eap-user-menu__trigger {
      border: none;
      background: transparent;
      padding: 0;
      cursor: pointer;
    }
    .eap-user-menu__dropdown {
      position: absolute;
      right: 0;
      top: calc(100% + 0.5rem);
      background: #fff;
      border: 1px solid #e2e4ec;
      border-radius: 0.5rem;
      box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
      min-width: 200px;
      z-index: 300;
      overflow: hidden;
    }
    .eap-user-menu__identity {
      padding: 0.75rem 0.875rem;
      border-bottom: 1px solid #e2e4ec;
    }
    .eap-user-menu__name {
      font-size: 0.8125rem;
      font-weight: 600;
      color: #1a1d29;
    }
    .eap-user-menu__email {
      font-size: 0.75rem;
      color: #8a8fa3;
    }
    .eap-user-menu__item {
      display: block;
      padding: 0.625rem 0.875rem;
      font-size: 0.875rem;
      cursor: pointer;

      &:hover {
        background-color: #eef0f5;
      }

      &.eap-user-menu__item--danger {
        color: #d64545;
      }
    }
  `
})
export class UserMenuComponent {
  protected readonly session = inject(AuthSessionService);

  protected readonly profilePath = `/${ROUTE_PATHS.profile}`;
  protected readonly settingsPath = `/${ROUTE_PATHS.settings}`;
  protected readonly logoutPath = `/${ROUTE_PATHS.auth.root}/${ROUTE_PATHS.auth.logout}`;

  private readonly _isOpen = signal(false);
  protected readonly isOpen = this._isOpen.asReadonly();

  protected toggle(): void {
    this._isOpen.update((open) => !open);
  }

  protected close(): void {
    this._isOpen.set(false);
  }
}
