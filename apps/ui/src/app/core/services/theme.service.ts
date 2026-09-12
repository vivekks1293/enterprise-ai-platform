import { Injectable, signal, effect } from '@angular/core';
import { STORAGE_KEYS } from '@core/constants/app.constants';

export type Theme = 'dark' | 'light';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly _theme = signal<Theme>(this.getInitialTheme());
  public readonly currentTheme = this._theme.asReadonly();

  constructor() {
    effect(() => {
      const theme = this._theme();
      document.body.classList.remove('dark-theme', 'light-theme');
      document.body.classList.add(`${theme}-theme`);
      localStorage.setItem(STORAGE_KEYS.theme, theme);
    });
  }

  public toggleTheme(): void {
    this._theme.update((t) => (t === 'dark' ? 'light' : 'dark'));
  }

  private getInitialTheme(): Theme {
    const saved = localStorage.getItem(STORAGE_KEYS.theme) as Theme | null;
    return saved === 'light' ? 'light' : 'dark';
  }
}

