import { ROUTE_PATHS } from '@core/constants/app.constants';

export interface NavItem {
  readonly label: string;
  readonly path: string;
  readonly icon: string; // bootstrap-icons class name, kept as string to avoid a hard icon-lib dependency
}

/**
 * Centralized nav model. Adding a future module (Prompt Library,
 * Knowledge Base, Analytics, Administration...) means adding one
 * entry here — the Sidebar component itself never changes.
 */
export const PRIMARY_NAV_ITEMS: readonly NavItem[] = [
  { label: 'Dashboard', path: `/${ROUTE_PATHS.dashboard}`, icon: 'bi-speedometer2' },
  { label: 'AI Chat', path: `/${ROUTE_PATHS.chat}`, icon: 'bi-chat-dots' },
  { label: 'Conversations', path: `/${ROUTE_PATHS.conversations}`, icon: 'bi-clock-history' },
  { label: 'Documents', path: `/${ROUTE_PATHS.documents}`, icon: 'bi-file-earmark-text' }
];

export const SECONDARY_NAV_ITEMS: readonly NavItem[] = [
  { label: 'Settings', path: `/${ROUTE_PATHS.settings}`, icon: 'bi-gear' },
  { label: 'Profile', path: `/${ROUTE_PATHS.profile}`, icon: 'bi-person-circle' }
];
