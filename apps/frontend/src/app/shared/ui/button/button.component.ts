import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UiSize, UiVariant } from '@shared/types/ui.types';

/**
 * Pure UI button. No business logic, no HTTP, no feature imports.
 * Wraps Bootstrap's btn classes so callers never write `class="btn btn-primary"` directly.
 */
@Component({
  selector: 'eap-button',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './button.component.html',
  styleUrl: './button.component.scss',
  host: {
    '[class.d-block]': 'fullWidth()'
  }
})
export class ButtonComponent {
  public readonly variant = input<UiVariant>('primary');
  public readonly size = input<UiSize>('md');
  public readonly disabled = input<boolean>(false);
  public readonly loading = input<boolean>(false);
  public readonly type = input<'button' | 'submit' | 'reset'>('button');
  public readonly fullWidth = input<boolean>(false);

  public readonly clicked = output<MouseEvent>();

  public onClick(event: MouseEvent): void {
    if (this.disabled() || this.loading()) {
      return;
    }
    this.clicked.emit(event);
  }
}
