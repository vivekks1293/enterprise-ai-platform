import { Routes } from '@angular/router';

export const CONVERSATIONS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/conversations-list.page').then((m) => m.ConversationsListPageComponent),
    title: 'Conversations'
  }
];
