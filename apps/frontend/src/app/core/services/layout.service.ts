import { Injectable, signal } from '@angular/core';
import { LAYOUT_DEFAULTS, STORAGE_KEYS } from '@core/constants/app.constants';

/**
 * Singleton layout state shared by the Shell (sidebar/header) so any
 * future feature can also react to layout changes (e.g. a chat panel
 * that needs to know how much horizontal space it has).
 */
@Injectable({ providedIn: 'root' })
export class LayoutService {
  private readonly _sidebarCollapsed = signal<boolean>(this.readInitialCollapsedState());
  private readonly _mobileSidebarOpen = signal<boolean>(false);

  public readonly sidebarCollapsed = this._sidebarCollapsed.asReadonly();
  public readonly mobileSidebarOpen = this._mobileSidebarOpen.asReadonly();

  public toggleSidebar(): void {
    this._sidebarCollapsed.update((collapsed) => {
      const next = !collapsed;
      localStorage.setItem(STORAGE_KEYS.sidebarCollapsed, String(next));
      return next;
    });
  }

  public toggleMobileSidebar(): void {
    this._mobileSidebarOpen.update((open) => !open);
  }

  public closeMobileSidebar(): void {
    this._mobileSidebarOpen.set(false);
  }

  private readInitialCollapsedState(): boolean {
    const stored = localStorage.getItem(STORAGE_KEYS.sidebarCollapsed);
    if (stored === null) {
      return LAYOUT_DEFAULTS.sidebarCollapsedByDefault;
    }
    return stored === 'true';
  }
}
