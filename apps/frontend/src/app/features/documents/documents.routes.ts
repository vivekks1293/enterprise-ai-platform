import { Routes } from '@angular/router';
import { PlaceholderPageComponent } from '@shared/ui/placeholder-page/placeholder-page.component';

export const DOCUMENTS_ROUTES: Routes = [
  {
    path: '',
    component: PlaceholderPageComponent,
    title: 'Documents',
    data: {
      title: 'Documents',
      description: 'Knowledge base file upload and management — scaffolded for the next sprint.'
    }
  }
];
