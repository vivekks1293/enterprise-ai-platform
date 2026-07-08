import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'eap-chip',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <span class="eap-chip">
      <ng-content></ng-content>
      @if (removable()) {
        <button type="button" class="eap-chip__remove" aria-label="Remove" (click)="removed.emit()">×</button>
      }
    </span>
  `,
  styles: `
    .eap-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.375rem;
      padding: 0.25rem 0.625rem;
      border-radius: 999px;
      background-color: var(--eap-bg-muted, #eef0f5);
      font-size: 0.8125rem;
    }
    .eap-chip__remove {
      border: none;
      background: transparent;
      cursor: pointer;
      line-height: 1;
      font-size: 1rem;
      padding: 0;
    }
  `
})
export class ChipComponent {
  public readonly removable = input<boolean>(false);
  public readonly removed = output<void>();
}
