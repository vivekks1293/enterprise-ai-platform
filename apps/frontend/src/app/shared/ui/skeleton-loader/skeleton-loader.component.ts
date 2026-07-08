import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'eap-skeleton-loader',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @for (row of rowsArray(); track row; let last = $last) {
      <div class="eap-skeleton" [style.height.px]="lineHeight()" [style.width]="last ? '70%' : '100%'"></div>
    }
  `,
  styles: `
    .eap-skeleton {
      background: linear-gradient(90deg, #eef0f5 25%, #e4e6ee 37%, #eef0f5 63%);
      background-size: 400% 100%;
      animation: eap-skeleton-shimmer 1.4s ease infinite;
      border-radius: 0.375rem;
      margin-bottom: 0.5rem;
    }
    @keyframes eap-skeleton-shimmer {
      0% {
        background-position: 100% 50%;
      }
      100% {
        background-position: 0 50%;
      }
    }
  `
})
export class SkeletonLoaderComponent {
  public readonly rows = input<number>(3);
  public readonly lineHeight = input<number>(16);

  protected rowsArray(): number[] {
    return Array.from({ length: this.rows() }, (_, i) => i);
  }
}
