/**
 * Thin, safe wrapper around localStorage so call sites don't need
 * try/catch for private-browsing/storage-disabled edge cases, and so
 * JSON parsing failures degrade gracefully instead of throwing.
 */
export const storageUtil = {
  getItem<T>(key: string): T | null {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : null;
    } catch {
      return null;
    }
  },

  setItem<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Storage unavailable (private mode, quota exceeded) — fail silently.
    }
  },

  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch {
      // no-op
    }
  }
};
