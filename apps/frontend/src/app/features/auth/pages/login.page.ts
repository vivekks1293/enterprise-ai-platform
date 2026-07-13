import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { CardComponent } from '@shared/ui/card/card.component';
import { InputComponent } from '@shared/ui/input/input.component';
import { ButtonComponent } from '@shared/ui/button/button.component';
import { AuthFacade } from '@features/auth/services/auth.facade';
import { AuthStateService } from '@features/auth/state/auth-state.service';
import { NotificationService } from '@core/services/notification.service';

/**
 * The only architectural rule this component follows: talk to
 * AuthFacade, nothing else. It never sees an ApiError, a DTO, or
 * touches AuthSessionService directly — it reads `facade.error()` for
 * a ready-to-display message and `facade.isSubmitting()` for loading UX.
 */
@Component({
  selector: 'eap-login-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CardComponent, InputComponent, ButtonComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [AuthStateService, AuthFacade],
  templateUrl: './login.page.html'
})
export class LoginPageComponent {
  protected readonly facade = inject(AuthFacade);
  private readonly fb = inject(FormBuilder);
  private readonly notifications = inject(NotificationService);

  protected readonly passwordVisible = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    // Placeholder only — not sent to the backend yet. Reserved for a
    // future "extend session length" flag once refresh-token support exists.
    rememberMe: [false]
  });

  protected togglePasswordVisibility(): void {
    this.passwordVisible.update((visible) => !visible);
  }

  protected onForgotPassword(): void {
    // Placeholder — no forgot-password flow exists yet.
    this.notifications.notify('Password reset isn’t available yet. Contact your administrator.', 'info');
  }

  protected onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { email, password } = this.form.getRawValue();
    this.facade.login({ email, password });
  }
}
