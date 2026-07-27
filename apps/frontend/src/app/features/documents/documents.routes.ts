import { Routes } from '@angular/router';

export const DOCUMENTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/documents.page').then((m) => m.DocumentsPageComponent),
    title: 'Documents'
  }
];
