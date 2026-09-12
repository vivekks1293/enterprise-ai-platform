import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService } from '@core/services/notification.service';
import { IconComponent } from './icon.component';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule, IconComponent],
  template: `
    <div class="toasts-anchor">
      @for (toast of notifications.toasts(); track toast.id) {
        <div class="toast-item" [attr.data-type]="toast.type">
          <div class="toast-icon">
            @switch (toast.type) {
              @case ('success') {
                <app-icon name="check" [size]="14"></app-icon>
              }
              @case ('error') {
                <app-icon name="alert-circle" [size]="14"></app-icon>
              }
              @default {
                <app-icon name="sparkles" [size]="14"></app-icon>
              }
            }
          </div>
          <span class="toast-message">{{ toast.message }}</span>
          <button type="button" class="toast-dismiss" (click)="notifications.dismiss(toast.id)">&times;</button>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .toasts-anchor {
        position: fixed;
        top: 1.25rem;
        right: 1.25rem;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        pointer-events: none;
      }

      .toast-item {
        pointer-events: auto;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        padding: 0.6rem 0.9rem;
        box-shadow: var(--shadow-md);
        font-size: 0.85rem;
        color: var(--text-primary);
        max-width: 380px;
        animation: slideIn 0.2s ease-out;

        &[data-type='success'] .toast-icon {
          color: var(--success);
        }
        &[data-type='error'] .toast-icon {
          color: var(--danger);
        }
        &[data-type='warning'] .toast-icon {
          color: var(--warning);
        }
      }

      .toast-icon {
        display: flex;
        align-items: center;
        flex-shrink: 0;
      }

      .toast-message {
        flex: 1;
        line-height: 1.35;
      }

      .toast-dismiss {
        font-size: 1.1rem;
        line-height: 1;
        color: var(--text-muted);
        padding: 0 0.2rem;
        &:hover {
          color: var(--text-primary);
        }
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(-8px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ToastComponent {
  public readonly notifications = inject(NotificationService);
}

