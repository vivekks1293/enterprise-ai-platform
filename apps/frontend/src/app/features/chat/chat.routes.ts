import { Routes } from '@angular/router';

export const CHAT_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/chat.page').then((m) => m.ChatPageComponent),
    title: 'AI Chat'
  },
  {
    path: ':conversationId',
    loadComponent: () => import('./pages/chat.page').then((m) => m.ChatPageComponent),
    title: 'AI Chat'
  }
];
