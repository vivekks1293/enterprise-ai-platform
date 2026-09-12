import { Component, ChangeDetectionStrategy, inject, signal, OnInit, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { AuthSessionService } from '@core/services/auth-session.service';
import { AuthRepository } from '@data/repositories/auth.repository';
import { ChatFacade } from '@features/chat/services/chat.facade';
import { ThemeService } from '@core/services/theme.service';
import { NotificationService } from '@core/services/notification.service';
import { IconComponent } from '@shared/components/icon.component';
import { ToastComponent } from '@shared/components/toast.component';
import { ROUTE_PATHS } from '@core/constants/app.constants';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, IconComponent, ToastComponent],
  template: `
    <div class="app-shell" [class.sidebar-collapsed]="isSidebarCollapsed()" [class.auth-route]="isAuthRoute()">
      <!-- Toast Overlay -->
      <app-toast></app-toast>

      @if (!isAuthRoute()) {
        <!-- Sleek Collapsible Sidebar -->
        <aside class="app-sidebar">
          <!-- Sidebar Top Brand -->
          <div class="sidebar-brand">
            <div class="brand-info">
              <div class="brand-badge">
                <app-icon name="sparkles" [size]="16"></app-icon>
              </div>
              @if (!isSidebarCollapsed()) {
                <span class="brand-name">OmniDoc</span>
              }
            </div>

            <button
              type="button"
              class="collapse-btn"
              (click)="toggleSidebar()"
              [title]="isSidebarCollapsed() ? 'Expand sidebar' : 'Collapse sidebar'"
            >
              <app-icon [name]="isSidebarCollapsed() ? 'chevron-right' : 'chevron-left'" [size]="14"></app-icon>
            </button>
          </div>

          <!-- New Chat Action -->
          <div class="new-chat-container">
            <button type="button" class="new-chat-btn" (click)="onNewChat()" title="Start New Conversation">
              <app-icon name="plus" [size]="16"></app-icon>
              @if (!isSidebarCollapsed()) {
                <span>New Chat</span>
              }
            </button>
          </div>

          <!-- Main Navigation Links -->
          <nav class="sidebar-nav">
            <a
              routerLink="/chat"
              routerLinkActive="active"
              [routerLinkActiveOptions]="{ exact: false }"
              class="nav-item"
              title="Chat Workspace"
            >
              <app-icon name="message-square" [size]="16"></app-icon>
              @if (!isSidebarCollapsed()) {
                <span>Chat</span>
              }
            </a>

            <a
              routerLink="/documents"
              routerLinkActive="active"
              class="nav-item"
              title="Knowledge Base & Documents"
            >
              <app-icon name="database" [size]="16"></app-icon>
              @if (!isSidebarCollapsed()) {
                <span>Knowledge Base</span>
              }
            </a>
          </nav>

          <!-- Conversation History (when expanded) -->
          @if (!isSidebarCollapsed()) {
            <div class="history-section">
              <div class="history-header">
                <span>Recent Conversations</span>
                <button
                  type="button"
                  class="refresh-history-btn"
                  (click)="chatFacade.loadConversations()"
                  [disabled]="chatFacade.isConversationsLoading()"
                  title="Refresh list"
                >
                  <app-icon
                    name="refresh-cw"
                    [class.spin-icon]="chatFacade.isConversationsLoading()"
                    [size]="12"
                  ></app-icon>
                </button>
              </div>

              <div class="history-list">
                @if (chatFacade.isConversationsLoading() && chatFacade.conversations().length === 0) {
                  <p class="no-history-hint">Loading conversations...</p>
                } @else if (chatFacade.conversations().length === 0) {
                  <p class="no-history-hint">No past conversations</p>
                } @else {
                  @for (c of chatFacade.conversations(); track c.id) {
                    <a
                      [routerLink]="['/chat', c.id]"
                      routerLinkActive="active-conversation"
                      class="history-item"
                      [title]="c.title"
                    >
                      <app-icon name="message-square" [size]="13"></app-icon>
                      <span class="conv-title">{{ c.title }}</span>
                    </a>
                  }
                }
              </div>
            </div>
          }

          <!-- Bottom User & Settings Bar -->
          <div class="sidebar-footer">
            <div class="user-profile">
              <div class="user-avatar" [title]="session.currentUser()?.email || 'User'">
                <app-icon name="user" [size]="15"></app-icon>
              </div>
              @if (!isSidebarCollapsed()) {
                <div class="user-details">
                  <span class="user-name">{{ session.currentUser()?.name || 'Workspace User' }}</span>
                  <span class="user-email">{{ session.currentUser()?.email }}</span>
                </div>
              }
            </div>

            <div class="footer-actions">
              <button
                type="button"
                class="footer-icon-btn"
                (click)="theme.toggleTheme()"
                [title]="theme.currentTheme() === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
              >
                <app-icon [name]="theme.currentTheme() === 'dark' ? 'sun' : 'moon'" [size]="15"></app-icon>
              </button>

              <button
                type="button"
                class="footer-icon-btn logout-btn"
                (click)="onLogout()"
                title="Sign Out"
              >
                <app-icon name="logout" [size]="15"></app-icon>
              </button>
            </div>
          </div>
        </aside>
      }

      <!-- Main Workspace Viewport -->
      <main class="app-main-canvas">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [
    `
      .app-shell {
        display: flex;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
        background: var(--bg-app);
      }

      .app-shell.auth-route {
        display: block;
      }

      .app-sidebar {
        width: 260px;
        height: 100%;
        background: var(--bg-sidebar);
        border-right: 1px solid var(--border-subtle);
        display: flex;
        flex-direction: column;
        transition: width var(--transition-smooth);
        flex-shrink: 0;
        z-index: 20;
      }

      .sidebar-collapsed .app-sidebar {
        width: 68px;
      }

      .sidebar-brand {
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 1rem;
        border-bottom: 1px solid var(--border-subtle);
      }

      .brand-info {
        display: flex;
        align-items: center;
        gap: 0.65rem;
      }

      .brand-badge {
        width: 30px;
        height: 30px;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, var(--primary), #8b5cf6);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px var(--primary-glow);
        flex-shrink: 0;
      }

      .brand-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
        white-space: nowrap;
      }

      .collapse-btn {
        width: 28px;
        height: 28px;
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        transition: all var(--transition-fast);

        &:hover {
          background: var(--bg-card);
          color: var(--text-primary);
        }
      }

      .new-chat-container {
        padding: 0.75rem 0.85rem 0.25rem 0.85rem;
      }

      .new-chat-btn {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        color: var(--text-primary);
        font-size: 0.88rem;
        font-weight: 600;
        padding: 0.6rem 0.85rem;
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);

        &:hover {
          background: var(--primary);
          border-color: var(--primary-light);
          color: #ffffff;
          box-shadow: 0 4px 12px var(--primary-glow);
        }
      }

      .sidebar-nav {
        padding: 0.5rem 0.85rem;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }

      .nav-item {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        font-size: 0.88rem;
        font-weight: 500;
        color: var(--text-secondary);
        padding: 0.5rem 0.75rem;
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);

        app-icon {
          color: var(--text-muted);
          transition: color var(--transition-fast);
        }

        &:hover {
          background: var(--bg-card);
          color: var(--text-primary);
          text-decoration: none;

          app-icon {
            color: var(--text-primary);
          }
        }

        &.active {
          background: var(--bg-chip);
          color: var(--primary-light);
          font-weight: 600;

          app-icon {
            color: var(--primary-light);
          }
        }
      }

      .history-section {
        flex: 1;
        overflow-y: auto;
        padding: 0.75rem 0.85rem;
        border-top: 1px solid var(--border-subtle);
        display: flex;
        flex-direction: column;
      }

      .history-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        padding: 0 0.25rem;
      }

      .refresh-history-btn {
        color: var(--text-muted);
        transition: color var(--transition-fast);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.2rem;
        border-radius: var(--radius-sm);

        &:hover:not(:disabled) {
          color: var(--text-primary);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }

      .spin-icon {
        display: inline-block;
        animation: spin 0.8s linear infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      .history-list {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
      }

      .no-history-hint {
        font-size: 0.78rem;
        color: var(--text-muted);
        font-style: italic;
        padding: 0.5rem 0.25rem;
      }

      .history-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.65rem;
        border-radius: var(--radius-sm);
        font-size: 0.82rem;
        color: var(--text-secondary);
        transition: all var(--transition-fast);
        white-space: nowrap;
        overflow: hidden;

        app-icon {
          color: var(--text-muted);
          flex-shrink: 0;
        }

        .conv-title {
          overflow: hidden;
          text-overflow: ellipsis;
        }

        &:hover {
          background: var(--bg-card);
          color: var(--text-primary);
          text-decoration: none;
        }

        &.active-conversation {
          background: var(--bg-card-hover);
          color: var(--primary-light);
          font-weight: 500;
          border-left: 2px solid var(--primary);
        }
      }

      .sidebar-footer {
        padding: 0.75rem 0.85rem;
        border-top: 1px solid var(--border-subtle);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
      }

      .user-profile {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        min-width: 0;
      }

      .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: var(--radius-full);
        background: var(--bg-card);
        border: 1px solid var(--border-default);
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      .user-details {
        min-width: 0;
        display: flex;
        flex-direction: column;
      }

      .user-name {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .user-email {
        font-size: 0.7rem;
        color: var(--text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .footer-actions {
        display: flex;
        align-items: center;
        gap: 0.25rem;
      }

      .footer-icon-btn {
        width: 28px;
        height: 28px;
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        transition: all var(--transition-fast);

        &:hover {
          background: var(--bg-card);
          color: var(--text-primary);
        }

        &.logout-btn:hover {
          color: var(--danger);
        }
      }

      .app-main-canvas {
        flex: 1;
        height: 100%;
        overflow: hidden;
        position: relative;
      }
    `
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AppComponent implements OnInit {
  public readonly session = inject(AuthSessionService);
  public readonly chatFacade = inject(ChatFacade);
  private readonly authRepo = inject(AuthRepository);
  public readonly theme = inject(ThemeService);
  private readonly router = inject(Router);
  private readonly toast = inject(NotificationService);

  public readonly isSidebarCollapsed = signal<boolean>(false);
  public readonly isAuthRoute = signal<boolean>(false);

  constructor() {
    effect(() => {
      const isAuth = this.session.isAuthenticated();
      if (isAuth) {
        this.chatFacade.loadConversations();
      } else {
        this.chatFacade.resetState();
      }
    });
  }

  public ngOnInit(): void {
    this.checkRoute(this.router.url);

    this.router.events.pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd)).subscribe((event) => {
      this.checkRoute(event.urlAfterRedirects);
    });
  }

  public toggleSidebar(): void {
    this.isSidebarCollapsed.update((v) => !v);
  }

  public onNewChat(): void {
    this.chatFacade.startNewChat();
  }

  public onLogout(): void {
    this.authRepo.logout().subscribe({
      next: () => {
        this.chatFacade.resetState();
        this.toast.info('Signed out');
        this.router.navigate([ROUTE_PATHS.login]);
      },
      error: () => {
        this.chatFacade.resetState();
        this.session.clearSession();
        this.router.navigate([ROUTE_PATHS.login]);
      }
    });
  }

  private checkRoute(url: string): void {
    this.isAuthRoute.set(url.includes('/login'));
  }
}

