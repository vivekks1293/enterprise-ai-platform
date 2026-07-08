import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UiVariant } from '@shared/types/ui.types';

@Component({
  selector: 'eap-badge',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <span
      class="badge"
      [class.text-bg-primary]="variant() === 'primary'"
      [class.text-bg-secondary]="variant() === 'secondary'"
      [class.text-bg-success]="variant() === 'success'"
      [class.text-bg-warning]="variant() === 'warning'"
      [class.text-bg-danger]="variant() === 'danger'"
      [class.text-bg-info]="variant() === 'info'"
    >
      <ng-content></ng-content>
    </span>
  `
})
export class BadgeComponent {
  public readonly variant = input<UiVariant>('secondary');
}
