import { Routes } from '@angular/router';
import { PlaceholderPageComponent } from '@shared/ui/placeholder-page/placeholder-page.component';

export const PROFILE_ROUTES: Routes = [
  {
    path: '',
    component: PlaceholderPageComponent,
    title: 'Profile',
    data: {
      title: 'Profile',
      description: 'User profile and preferences — scaffolded for the next sprint.'
    }
  }
];
