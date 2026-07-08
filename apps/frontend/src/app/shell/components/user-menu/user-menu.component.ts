import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AvatarComponent } from '@shared/ui/avatar/avatar.component';
import { ClickOutsideDirective } from '@shared/directives/click-outside.directive';

@Component({
  selector: 'eap-user-menu',
  standalone: true,
  imports: [CommonModule, AvatarComponent, ClickOutsideDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-user-menu" (eapClickOutside)="close()">
      <button type="button" class="eap-user-menu__trigger" (click)="toggle()" aria-haspopup="true" [attr.aria-expanded]="isOpen()">
        <eap-avatar name="Vivek Kumar" size="sm"></eap-avatar>
      </button>
      @if (isOpen()) {
        <div class="eap-user-menu__dropdown" role="menu">
          <a class="eap-user-menu__item" role="menuitem">Profile</a>
          <a class="eap-user-menu__item" role="menuitem">Settings</a>
          <a class="eap-user-menu__item" role="menuitem">Sign out</a>
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
      min-width: 180px;
      z-index: 300;
      overflow: hidden;
    }
    .eap-user-menu__item {
      display: block;
      padding: 0.625rem 0.875rem;
      font-size: 0.875rem;
      cursor: pointer;

      &:hover {
        background-color: #eef0f5;
      }
    }
  `
})
export class UserMenuComponent {
  private readonly _isOpen = signal(false);
  protected readonly isOpen = this._isOpen.asReadonly();

  protected toggle(): void {
    this._isOpen.update((open) => !open);
  }

  protected close(): void {
    this._isOpen.set(false);
  }
}
