import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

/**
 * Zero-chrome layout for full-bleed screens (print/export views,
 * embedded widgets, error pages). Distinct from AuthLayout so the
 * two can diverge independently as needs emerge.
 */
@Component({
  selector: 'eap-blank-layout',
  standalone: true,
  imports: [RouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<router-outlet></router-outlet>`
})
export class BlankLayoutComponent {}
