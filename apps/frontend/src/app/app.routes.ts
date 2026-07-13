import { Routes } from '@angular/router';
import { ROUTE_PATHS } from '@core/constants/app.constants';
import { authGuard } from '@core/guards/auth.guard';
import { AppLayoutComponent } from '@shell/layouts/app-layout/app-layout.component';
import { AuthLayoutComponent } from '@shell/layouts/auth-layout/auth-layout.component';

/**
 * Root routing table. Each feature owns its own `*.routes.ts` file
 * (see features/<name>/<name>.routes.ts) — this file only wires
 * layouts to lazy-loaded feature route groups. No feature route
 * definitions live here directly.
 */
export const APP_ROUTES: Routes = [
  {
    path: ROUTE_PATHS.auth.root,
    component: AuthLayoutComponent,
    loadChildren: () => import('@features/auth/auth.routes').then((m) => m.AUTH_ROUTES)
  },
  {
    path: '',
    component: AppLayoutComponent,
    // Gates every child route below — a single guard declaration here
    // protects Dashboard, Chat, Conversations, Documents, Settings,
    // and Profile alike, and any future feature added as a child
    // inherits the same protection automatically.
    canActivateChild: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: ROUTE_PATHS.dashboard },
      {
        path: ROUTE_PATHS.dashboard,
        loadChildren: () => import('@features/dashboard/dashboard.routes').then((m) => m.DASHBOARD_ROUTES)
      },
      {
        path: ROUTE_PATHS.chat,
        loadChildren: () => import('@features/chat/chat.routes').then((m) => m.CHAT_ROUTES)
      },
      {
        path: ROUTE_PATHS.conversations,
        loadChildren: () =>
          import('@features/conversations/conversations.routes').then((m) => m.CONVERSATIONS_ROUTES)
      },
      {
        path: ROUTE_PATHS.documents,
        loadChildren: () => import('@features/documents/documents.routes').then((m) => m.DOCUMENTS_ROUTES)
      },
      {
        path: ROUTE_PATHS.settings,
        loadChildren: () => import('@features/settings/settings.routes').then((m) => m.SETTINGS_ROUTES)
      },
      {
        path: ROUTE_PATHS.profile,
        loadChildren: () => import('@features/profile/profile.routes').then((m) => m.PROFILE_ROUTES)
      }
    ]
  },
  { path: '**', redirectTo: ROUTE_PATHS.dashboard }
];
