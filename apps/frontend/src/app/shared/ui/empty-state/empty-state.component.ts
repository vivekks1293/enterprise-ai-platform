import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'eap-empty-state',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-empty-state">
      <div class="eap-empty-state__icon">
        <ng-content select="[icon]"></ng-content>
      </div>
      <h4 class="eap-empty-state__title">{{ title() }}</h4>
      @if (description()) {
        <p class="eap-empty-state__description">{{ description() }}</p>
      }
      <ng-content select="[actions]"></ng-content>
    </div>
  `,
  styles: `
    .eap-empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 3rem 1.5rem;
      color: var(--eap-text-secondary, #5b6072);
    }
    .eap-empty-state__title {
      margin: 0.5rem 0 0.25rem;
    }
    .eap-empty-state__description {
      margin: 0 0 1rem;
      max-width: 360px;
    }
  `
})
export class EmptyStateComponent {
  public readonly title = input<string>('Nothing here yet');
  public readonly description = input<string | undefined>(undefined);
}
