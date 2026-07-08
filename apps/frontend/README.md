# Enterprise AI Platform — Frontend Foundation (Sprint 1)

Angular 18 (standalone components), TypeScript strict mode, Bootstrap 5, SCSS.
This is the frontend **foundation** only — no backend, auth logic, or AI integration.
Everything here is built so 100+ future screens can be added without restructuring.

## Getting started

```bash
npm install
npm start          # dev server
npm run build:prod # production build
npm run lint
```

## Architecture at a glance

```
Component → Facade → Repository → ApiClient → Backend
```

- **Components** never inject `HttpClient` or a Repository directly — only a Facade.
- **Facades** (`features/<name>/services/*.facade.ts`) own orchestration between
  feature-local state and the data layer. One Facade + one State service per feature,
  provided at the route level (not root) so they reset when the feature unloads.
- **Repositories** (`data/repositories`) are the only place that know about DTOs
  and mappers. They return domain models, never raw wire data.
- **ApiClient** (`data/api/api-client.service.ts`) is the *only* class allowed to
  call `HttpClient` directly.

See `features/conversations` for the fully-wired reference implementation of this
pattern (facade, state, repository, DTO, mapper, mock data fallback). Every other
future feature should copy that shape.

## Folder structure

- `core/` — singleton services, guards, interceptors, global error handling,
  app-wide constants/tokens. No UI components live here.
- `shared/` — reusable, business-logic-free UI (`shared/ui`), directives, pipes,
  models, types, validators. Anything here must work in any future feature.
- `features/<name>/` — one folder per feature module (`pages/`, `components/`,
  `services/`, `models/`, `state/`, `<name>.routes.ts`). Features are lazy-loaded
  and do not import from one another.
- `data/` — API client, repositories, DTOs, mappers. The data layer's own
  internal architecture, separate from feature-local models.
- `shell/` — sidebar, header, breadcrumbs, user menu, and the three layouts
  (App/Auth/Blank). Shell has zero knowledge of any feature's business logic.
- `styles/` — enterprise SCSS architecture (abstracts → base → layout →
  components → themes → utilities). All design tokens live in
  `styles/abstracts/_variables.scss` — never hardcode a spacing/color/z-index
  value anywhere else.

## Routing

Every feature owns `<name>.routes.ts` and is lazy-loaded via `loadChildren` /
`loadComponent` from `app.routes.ts`. There is no single giant route file.
`withComponentInputBinding()` is enabled, so route `data` can bind directly to
component `input()`s (see the placeholder-backed features: chat, documents,
settings, profile).

## Styling rules

- Bootstrap utilities are wrapped in semantic classes (`page-container`,
  `content-wrapper`, `section-card`, `page-header`, `page-content`) defined in
  `styles/layout/_grid.scss` — templates should reach for these before raw
  Bootstrap grid/utility classes.
- All shared UI components (`shared/ui/*`) are business-logic-free and reusable
  forever: Button, Card, Input, Spinner, Avatar, Badge, Chip, EmptyState,
  LoadingState, ErrorState, SkeletonLoader, SearchBox, Modal, PlaceholderPage.

## State management

Angular Signals for local UI/feature state. RxJS for async flows and streams
(e.g. debounced search, HTTP). No NgRx — intentionally, per scope. Introduce it
only if a feature's state genuinely outgrows Signals + a Facade.

## Theming

Light theme is fully implemented via CSS custom properties
(`styles/themes/_light.scss`) driven by design tokens. Dark theme
(`styles/themes/_dark.scss`) and `ThemeService` are architecturally wired
(`data-theme` attribute toggle) but intentionally left unpolished per scope.

## What's real vs. scaffolded in this sprint

**Fully implemented:** shell (sidebar/header/breadcrumbs/user menu), all three
layouts, routing, SCSS/design-token system, shared UI kit, Dashboard, Login page
(UI only), Conversations (full Component→Facade→Repository chain with mock data).

**Scaffolded placeholders** (route + page exist, ready for real implementation):
AI Chat, Documents, Settings, Profile. Wiring up their real UI is a matter of
following the Conversations pattern — no architectural changes needed.
