import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UiSize } from '@shared/types/ui.types';

@Component({
  selector: 'eap-modal',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (open()) {
      <div class="eap-modal-backdrop" (click)="closed.emit()">
        <div
          class="eap-modal"
          [class.eap-modal--sm]="size() === 'sm'"
          [class.eap-modal--lg]="size() === 'lg'"
          role="dialog"
          aria-modal="true"
          [attr.aria-label]="title()"
          (click)="$event.stopPropagation()"
        >
          <div class="eap-modal__header">
            <h3 class="eap-modal__title">{{ title() }}</h3>
            <button type="button" class="eap-modal__close" aria-label="Close" (click)="closed.emit()">×</button>
          </div>
          <div class="eap-modal__body">
            <ng-content></ng-content>
          </div>
          <div class="eap-modal__footer">
            <ng-content select="[modalFooter]"></ng-content>
          </div>
        </div>
      </div>
    }
  `,
  styles: `
    .eap-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(16, 24, 40, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 400;
    }
    .eap-modal {
      background: #fff;
      border-radius: 0.75rem;
      width: 480px;
      max-width: calc(100vw - 2rem);
      max-height: calc(100vh - 4rem);
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 32px rgba(16, 24, 40, 0.12);

      &.eap-modal--sm {
        width: 360px;
      }
      &.eap-modal--lg {
        width: 720px;
      }
    }
    .eap-modal__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 1.25rem;
      border-bottom: 1px solid #e2e4ec;
    }
    .eap-modal__title {
      margin: 0;
      font-size: 1.125rem;
    }
    .eap-modal__close {
      border: none;
      background: transparent;
      font-size: 1.25rem;
      cursor: pointer;
      line-height: 1;
    }
    .eap-modal__body {
      padding: 1.25rem;
      overflow-y: auto;
    }
    .eap-modal__footer {
      padding: 1rem 1.25rem;
      border-top: 1px solid #e2e4ec;
    }
  `
})
export class ModalComponent {
  public readonly open = input<boolean>(false);
  public readonly title = input<string>('');
  public readonly size = input<UiSize>('md');
  public readonly closed = output<void>();
}
