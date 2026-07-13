/**
 * Route path segments used across the app shell and feature routing.
 * Centralized so route strings are never duplicated or hardcoded
 * inline inside templates or navigation configs.
 */
export const ROUTE_PATHS = {
  auth: {
    root: 'auth',
    login: 'login',
    logout: 'logout'
  },
  dashboard: 'dashboard',
  chat: 'chat',
  conversations: 'conversations',
  documents: 'documents',
  settings: 'settings',
  profile: 'profile'
} as const;

/** Keys used for browser storage — kept in one place to avoid typos/collisions. */
export const STORAGE_KEYS = {
  theme: 'eap.theme',
  sidebarCollapsed: 'eap.sidebar.collapsed',
  authToken: 'eap.auth.token',
  authUser: 'eap.auth.user',
  authExpiresAt: 'eap.auth.expiresAt'
} as const;

/** Default layout values not already covered by SCSS design tokens. */
export const LAYOUT_DEFAULTS = {
  sidebarCollapsedByDefault: false,
  toastDurationMs: 4000
} as const;
