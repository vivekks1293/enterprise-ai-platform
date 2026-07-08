import { Routes } from '@angular/router';
import { ROUTE_PATHS } from '@core/constants/app.constants';

export const AUTH_ROUTES: Routes = [
  {
    path: ROUTE_PATHS.auth.login,
    loadComponent: () => import('./pages/login.page').then((m) => m.LoginPageComponent),
    title: 'Sign in'
  },
  { path: '', pathMatch: 'full', redirectTo: ROUTE_PATHS.auth.login }
];
