import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutService } from '@core/services/layout.service';
import { NotificationService } from '@core/services/notification.service';
import { BreadcrumbsComponent } from '@shell/components/breadcrumbs/breadcrumbs.component';
import { UserMenuComponent } from '@shell/components/user-menu/user-menu.component';
import { BadgeComponent } from '@shared/ui/badge/badge.component';

@Component({
  selector: 'eap-header',
  standalone: true,
  imports: [CommonModule, BreadcrumbsComponent, UserMenuComponent, BadgeComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './header.component.html'
})
export class HeaderComponent {
  protected readonly layout = inject(LayoutService);
  protected readonly notifications = inject(NotificationService);
}
