import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SpinnerComponent } from '@shared/ui/spinner/spinner.component';

@Component({
  selector: 'eap-loading-state',
  standalone: true,
  imports: [CommonModule, SpinnerComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-loading-state">
      <eap-spinner size="lg" [label]="message()"></eap-spinner>
      <p class="eap-loading-state__message">{{ message() }}</p>
    </div>
  `,
  styles: `
    .eap-loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.75rem;
      padding: 3rem 1.5rem;
      color: var(--eap-text-secondary, #5b6072);
    }
  `
})
export class LoadingStateComponent {
  public readonly message = input<string>('Loading…');
}
