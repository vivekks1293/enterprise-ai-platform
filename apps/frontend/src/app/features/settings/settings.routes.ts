import { Routes } from '@angular/router';
import { PlaceholderPageComponent } from '@shared/ui/placeholder-page/placeholder-page.component';

export const SETTINGS_ROUTES: Routes = [
  {
    path: '',
    component: PlaceholderPageComponent,
    title: 'Settings',
    data: {
      title: 'Settings',
      description: 'Workspace, theme, and account settings — scaffolded for the next sprint.'
    }
  }
];
