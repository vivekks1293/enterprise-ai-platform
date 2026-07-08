import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

/**
 * Minimal layout for unauthenticated screens (login, forgot password,
 * SSO callback). No sidebar, no header — those screens own their
 * entire viewport.
 */
@Component({
  selector: 'eap-auth-layout',
  standalone: true,
  imports: [RouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<router-outlet></router-outlet>`
})
export class AuthLayoutComponent {}
