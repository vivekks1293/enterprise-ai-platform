import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardComponent } from '@shared/ui/card/card.component';

/**
 * Used by features whose real screens haven't been built yet
 * (Settings, Profile, Admin, etc.). Keeps every route in the app
 * navigable today, so the Shell/navigation can be demoed end-to-end
 * without waiting on every feature's real implementation.
 */
@Component({
  selector: 'eap-placeholder-page',
  standalone: true,
  imports: [CommonModule, CardComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="page-container">
      <div class="content-wrapper">
        <div class="page-header">
          <div>
            <h1>{{ title() }}</h1>
            <p class="text-secondary-eap">{{ description() }}</p>
          </div>
        </div>
        <div class="page-content">
          <eap-card>
            <p class="text-muted-eap mb-0">This module is scaffolded and ready for implementation.</p>
          </eap-card>
        </div>
      </div>
    </div>
  `
})
export class PlaceholderPageComponent {
  public readonly title = input<string>('Coming soon');
  public readonly description = input<string>('This section is under construction.');
}
