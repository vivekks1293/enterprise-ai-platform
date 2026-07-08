import { Injectable, signal } from '@angular/core';

export interface Breadcrumb {
  readonly label: string;
  readonly path?: string;
}

/**
 * Cross-cutting UI state that isn't "owned" by any single feature —
 * e.g. the breadcrumb trail, which a feature page sets but the Shell
 * renders. Feature-local state (chat messages, document lists, etc.)
 * belongs inside `features/<name>/state`, not here.
 */
@Injectable({ providedIn: 'root' })
export class GlobalUiStateService {
  private readonly _breadcrumbs = signal<readonly Breadcrumb[]>([]);
  private readonly _pageTitle = signal<string>('');

  public readonly breadcrumbs = this._breadcrumbs.asReadonly();
  public readonly pageTitle = this._pageTitle.asReadonly();

  public setBreadcrumbs(breadcrumbs: readonly Breadcrumb[]): void {
    this._breadcrumbs.set(breadcrumbs);
  }

  public setPageTitle(title: string): void {
    this._pageTitle.set(title);
  }
}
