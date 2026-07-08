import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UiSize } from '@shared/types/ui.types';

@Component({
  selector: 'eap-avatar',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-avatar" [class.eap-avatar--sm]="size() === 'sm'" [class.eap-avatar--lg]="size() === 'lg'">
      @if (imageUrl()) {
        <img [src]="imageUrl()" [alt]="name()" />
      } @else {
        <span>{{ initials() }}</span>
      }
    </div>
  `,
  styles: `
    .eap-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background-color: var(--bs-primary);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 0.8125rem;
      overflow: hidden;
      flex-shrink: 0;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      &.eap-avatar--sm {
        width: 28px;
        height: 28px;
        font-size: 0.6875rem;
      }

      &.eap-avatar--lg {
        width: 48px;
        height: 48px;
        font-size: 1rem;
      }
    }
  `
})
export class AvatarComponent {
  public readonly name = input<string>('');
  public readonly imageUrl = input<string | undefined>(undefined);
  public readonly size = input<UiSize>('md');

  public readonly initials = computed(() =>
    this.name()
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join('')
  );
}
