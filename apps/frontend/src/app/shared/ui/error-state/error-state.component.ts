import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonComponent } from '@shared/ui/button/button.component';

@Component({
  selector: 'eap-error-state',
  standalone: true,
  imports: [CommonModule, ButtonComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-error-state" role="alert">
      <h4 class="eap-error-state__title">{{ title() }}</h4>
      <p class="eap-error-state__description">{{ description() }}</p>
      @if (retryable()) {
        <eap-button variant="secondary" (clicked)="retry.emit()">Try again</eap-button>
      }
    </div>
  `,
  styles: `
    .eap-error-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 3rem 1.5rem;
    }
    .eap-error-state__title {
      color: var(--bs-danger);
    }
    .eap-error-state__description {
      color: var(--eap-text-secondary, #5b6072);
      margin: 0.25rem 0 1rem;
      max-width: 360px;
    }
  `
})
export class ErrorStateComponent {
  public readonly title = input<string>('Something went wrong');
  public readonly description = input<string>('Please try again in a moment.');
  public readonly retryable = input<boolean>(true);
  public readonly retry = output<void>();
}
