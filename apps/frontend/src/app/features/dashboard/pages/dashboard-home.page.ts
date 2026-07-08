import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardComponent } from '@shared/ui/card/card.component';
import { BadgeComponent } from '@shared/ui/badge/badge.component';

interface DashboardStat {
  readonly label: string;
  readonly value: string;
  readonly trend: string;
  readonly trendVariant: 'success' | 'danger';
}

@Component({
  selector: 'eap-dashboard-home-page',
  standalone: true,
  imports: [CommonModule, CardComponent, BadgeComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './dashboard-home.page.html'
})
export class DashboardHomePageComponent {
  protected readonly stats: readonly DashboardStat[] = [
    { label: 'Active Conversations', value: '128', trend: '+12%', trendVariant: 'success' },
    { label: 'Documents Indexed', value: '3,402', trend: '+4%', trendVariant: 'success' },
    { label: 'Avg. Response Time', value: '1.8s', trend: '-8%', trendVariant: 'success' },
    { label: 'Failed Queries', value: '6', trend: '+2', trendVariant: 'danger' }
  ];
}
