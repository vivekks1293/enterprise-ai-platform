import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthRepository } from '@data/repositories/auth.repository';
import { NotificationService } from '@core/services/notification.service';
import { IconComponent } from '@shared/components/icon.component';
import { ROUTE_PATHS } from '@core/constants/app.constants';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, IconComponent],
  template: `
    <div class="login-wrapper">
      <div class="login-card">
        <div class="brand-header">
          <div class="brand-icon">
            <app-icon name="sparkles" [size]="24"></app-icon>
          </div>
          <h1>Enterprise AI</h1>
          <p class="brand-tagline">Secure, grounded intelligence workspace</p>
        </div>

        <form (ngSubmit)="onSubmit()" class="login-form">
          <div class="input-group">
            <label for="email">Work Email</label>
            <div class="input-field-wrapper">
              <input
                id="email"
                type="email"
                name="email"
                [(ngModel)]="email"
                placeholder="name@enterprise.com"
                required
                [disabled]="isLoading()"
              />
            </div>
          </div>

          <div class="input-group">
            <label for="password">Password</label>
            <div class="input-field-wrapper">
              <input
                id="password"
                type="password"
                name="password"
                [(ngModel)]="password"
                placeholder="••••••••••••"
                required
                [disabled]="isLoading()"
              />
            </div>
          </div>

          <button type="submit" class="submit-btn" [disabled]="isLoading() || !isValid()">
            @if (isLoading()) {
              <div class="spinner"></div>
              <span>Signing in...</span>
            } @else {
              <span>Sign In to Workspace</span>
            }
          </button>
        </form>

        <div class="card-footer">
          <span>Enterprise AI Platform • Version 1.0</span>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        height: 100vh;
      }

      .login-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        background: radial-gradient(ellipse at top, #161f30 0%, var(--bg-app) 70%);
        padding: 1.5rem;
      }

      .login-card {
        width: 100%;
        max-width: 420px;
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-xl);
        padding: 2.5rem 2rem;
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(20px);
      }

      .brand-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 2rem;
      }

      .brand-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-lg);
        background: linear-gradient(135deg, var(--primary), #8b5cf6);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px var(--primary-glow);
      }

      h1 {
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;
      }

      .brand-tagline {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
      }

      .login-form {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
      }

      .input-group {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;

        label {
          font-size: 0.82rem;
          font-weight: 500;
          color: var(--text-secondary);
        }
      }

      .input-field-wrapper {
        background: var(--bg-input);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 0.65rem 0.85rem;
        transition: all var(--transition-fast);

        &:focus-within {
          border-color: var(--primary);
          box-shadow: 0 0 0 1px var(--primary);
        }

        input {
          width: 100%;
          font-size: 0.92rem;
          color: var(--text-primary);
          &::placeholder {
            color: var(--text-muted);
          }
        }
      }

      .submit-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        background: var(--primary);
        color: #ffffff;
        font-size: 0.92rem;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: var(--radius-md);
        margin-top: 0.5rem;
        transition: all var(--transition-fast);
        box-shadow: 0 4px 12px var(--primary-glow);

        &:hover:not(:disabled) {
          background: var(--primary-hover);
          transform: translateY(-1px);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          box-shadow: none;
        }
      }

      .spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }

      .card-footer {
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-subtle);
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class LoginComponent {
  private readonly authRepo = inject(AuthRepository);
  private readonly router = inject(Router);
  private readonly toast = inject(NotificationService);

  public email = '';
  public password = '';
  public readonly isLoading = signal<boolean>(false);

  public isValid(): boolean {
    return this.email.trim().length > 3 && this.password.trim().length > 3;
  }

  public onSubmit(): void {
    if (!this.isValid() || this.isLoading()) return;

    this.isLoading.set(true);
    this.authRepo.login({ email: this.email.trim(), password: this.password }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.toast.success('Welcome back!');
        this.router.navigate([ROUTE_PATHS.chat]);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.toast.error(err?.error?.detail || 'Invalid email or password');
      }
    });
  }
}

