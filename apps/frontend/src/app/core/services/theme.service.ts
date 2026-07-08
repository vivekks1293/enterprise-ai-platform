import { Injectable, signal, effect } from '@angular/core';
import { STORAGE_KEYS } from '@core/constants/app.constants';

export type ThemeMode = 'light' | 'dark';

/**
 * Owns the active theme as a signal and reflects it onto the
 * `data-theme` attribute on <html>, which the SCSS theme partials
 * (styles/themes/_light.scss, _dark.scss) key off of. Dark mode is
 * architecturally wired but intentionally left unpolished per scope.
 */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly _theme = signal<ThemeMode>(this.readInitialTheme());
  public readonly theme = this._theme.asReadonly();

  constructor() {
    effect(() => {
      const mode = this._theme();
      document.documentElement.setAttribute('data-theme', mode);
      localStorage.setItem(STORAGE_KEYS.theme, mode);
    });
  }

  public setTheme(mode: ThemeMode): void {
    this._theme.set(mode);
  }

  public toggleTheme(): void {
    this._theme.update((current) => (current === 'light' ? 'dark' : 'light'));
  }

  private readInitialTheme(): ThemeMode {
    const stored = localStorage.getItem(STORAGE_KEYS.theme);
    return stored === 'dark' ? 'dark' : 'light';
  }
}
