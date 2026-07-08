import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LayoutService } from '@core/services/layout.service';
import { PRIMARY_NAV_ITEMS, SECONDARY_NAV_ITEMS } from '@shell/navigation/nav-config';

@Component({
  selector: 'eap-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './sidebar.component.html'
})
export class SidebarComponent {
  protected readonly layout = inject(LayoutService);

  protected readonly primaryNavItems = PRIMARY_NAV_ITEMS;
  protected readonly secondaryNavItems = SECONDARY_NAV_ITEMS;
}
