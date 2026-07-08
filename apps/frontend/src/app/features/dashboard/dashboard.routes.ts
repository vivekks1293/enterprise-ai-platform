import { Routes } from '@angular/router';

export const DASHBOARD_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/dashboard-home.page').then((m) => m.DashboardHomePageComponent),
    title: 'Dashboard'
  }
];
