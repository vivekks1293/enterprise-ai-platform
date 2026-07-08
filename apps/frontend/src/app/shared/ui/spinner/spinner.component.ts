import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UiSize } from '@shared/types/ui.types';

@Component({
  selector: 'eap-spinner',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div
      class="spinner-border"
      [class.spinner-border-sm]="size() === 'sm'"
      role="status"
      [attr.aria-label]="label()"
    >
      <span class="visually-hidden-eap">{{ label() }}</span>
    </div>
  `
})
export class SpinnerComponent {
  public readonly size = input<UiSize>('md');
  public readonly label = input<string>('Loading');
}
