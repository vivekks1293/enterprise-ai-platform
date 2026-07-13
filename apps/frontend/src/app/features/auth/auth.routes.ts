import { Routes } from '@angular/router';
import { ROUTE_PATHS } from '@core/constants/app.constants';
import { guestGuard } from '@core/guards/guest.guard';

export const AUTH_ROUTES: Routes = [
  {
    path: ROUTE_PATHS.auth.login,
    loadComponent: () => import('./pages/login.page').then((m) => m.LoginPageComponent),
    // An already-authenticated user shouldn't see the login form again.
    canActivate: [guestGuard],
    title: 'Sign in'
  },
  {
    path: ROUTE_PATHS.auth.logout,
    loadComponent: () => import('./pages/logout.page').then((m) => m.LogoutPageComponent),
    title: 'Signing out'
  },
  { path: '', pathMatch: 'full', redirectTo: ROUTE_PATHS.auth.login }
];
