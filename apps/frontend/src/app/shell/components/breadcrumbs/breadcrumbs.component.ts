import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { GlobalUiStateService } from '@core/state/global-ui-state.service';

@Component({
  selector: 'eap-breadcrumbs',
  standalone: true,
  imports: [CommonModule, RouterModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (uiState.breadcrumbs().length > 0) {
      <nav aria-label="Breadcrumb" class="eap-breadcrumbs">
        <ol>
          @for (crumb of uiState.breadcrumbs(); track crumb.label; let last = $last) {
            <li>
              @if (crumb.path && !last) {
                <a [routerLink]="crumb.path">{{ crumb.label }}</a>
              } @else {
                <span aria-current="page">{{ crumb.label }}</span>
              }
            </li>
          }
        </ol>
      </nav>
    }
  `,
  styles: `
    .eap-breadcrumbs ol {
      display: flex;
      gap: 0.5rem;
      font-size: 0.8125rem;
      color: var(--eap-text-secondary, #5b6072);
    }
    .eap-breadcrumbs li:not(:last-child)::after {
      content: '/';
      margin-left: 0.5rem;
      color: var(--eap-text-secondary, #5b6072);
    }
    .eap-breadcrumbs li {
      display: flex;
    }
  `
})
export class BreadcrumbsComponent {
  protected readonly uiState = inject(GlobalUiStateService);
}
