import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthFacade } from '@features/auth/services/auth.facade';
import { AuthStateService } from '@features/auth/state/auth-state.service';
import { LoadingStateComponent } from '@shared/ui/loading-state/loading-state.component';

/**
 * This is how the Shell triggers a real logout without ever importing
 * `features/auth` — `UserMenuComponent`'s "Sign out" link just points
 * at the `/auth/logout` URL (see shell/components/user-menu). Only a
 * route string crosses the Shell→Feature boundary, never a class
 * import, which is what keeps "Shell has zero feature knowledge" true
 * even though Shell needs to expose a working sign-out control.
 */
@Component({
  selector: 'eap-logout-page',
  standalone: true,
  imports: [CommonModule, LoadingStateComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [AuthStateService, AuthFacade],
  template: `
    <div class="eap-auth-page">
      <eap-loading-state message="Signing you out…"></eap-loading-state>
    </div>
  `
})
export class LogoutPageComponent implements OnInit {
  private readonly facade = inject(AuthFacade);

  public ngOnInit(): void {
    this.facade.logout();
  }
}
