import { Routes } from '@angular/router';
import { PlaceholderPageComponent } from '@shared/ui/placeholder-page/placeholder-page.component';

export const CHAT_ROUTES: Routes = [
  {
    path: '',
    component: PlaceholderPageComponent,
    title: 'AI Chat',
    data: {
      title: 'AI Chat',
      description: 'Streaming AI chat with citations — scaffolded for the next sprint.'
    }
  }
];
