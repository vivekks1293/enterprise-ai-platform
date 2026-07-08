import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from '@shell/components/sidebar/sidebar.component';
import { HeaderComponent } from '@shell/components/header/header.component';

/**
 * The primary authenticated-app layout: sidebar + header + routed
 * content. Feature routes that should render inside the app chrome
 * are nested under this layout's route (see app.routes.ts).
 */
@Component({
  selector: 'eap-app-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent, HeaderComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="eap-app-shell">
      <eap-sidebar></eap-sidebar>
      <div class="eap-app-shell__main">
        <eap-header></eap-header>
        <router-outlet></router-outlet>
      </div>
    </div>
  `
})
export class AppLayoutComponent {}
