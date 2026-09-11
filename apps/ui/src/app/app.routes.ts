import { Routes } from '@angular/router';
import { authGuard } from '@core/guards/auth.guard';
import { ROUTE_PATHS } from '@core/constants/app.constants';

export const routes: Routes = [
  {
    path: ROUTE_PATHS.login,
    loadComponent: () => import('@features/auth/login.component').then((m) => m.LoginComponent)
  },
  {
    path: ROUTE_PATHS.chat,
    canActivate: [authGuard],
    loadComponent: () => import('@features/chat/chat.component').then((m) => m.ChatComponent)
  },
  {
    path: `${ROUTE_PATHS.chat}/:id`,
    canActivate: [authGuard],
    loadComponent: () => import('@features/chat/chat.component').then((m) => m.ChatComponent)
  },
  {
    path: ROUTE_PATHS.documents,
    canActivate: [authGuard],
    loadComponent: () => import('@features/documents/documents.component').then((m) => m.DocumentsComponent)
  },
  {
    path: '**',
    redirectTo: ROUTE_PATHS.chat
  }
];

