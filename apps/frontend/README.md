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
Component → Facade → Repository → Feature API Service → ApiClient → Backend
```

- **Components** never inject `HttpClient`, a Repository, or an API Service
  directly — only a Facade.
- **Facades** (`features/<name>/services/*.facade.ts`) own orchestration between
  feature-local state and the data layer. One Facade + one State service per feature,
  provided at the route level (not root) so they reset when the feature unloads.
- **Repositories** (`data/repositories`) decide *where* data comes from (REST
  today; cache/offline storage later) and own DTO→domain mapping. They return
  domain models, never raw wire data.
- **Feature API Services** (`data/api-services`) know endpoint paths and DTO
  shapes for one feature — no business logic, no UI concerns.
- **ApiClient** (`data/api/api-client.service.ts`) is the *only* class allowed to
  call `HttpClient` directly.

See `features/conversations` for the fully-wired reference implementation of this
pattern (facade, state, repository, API service, DTO, mapper, mock data fallback).
Every other future feature should copy that shape. See "Communication layer"
below for the streaming/error-handling infrastructure added in Sprint 1B.

## Folder structure

- `core/` — singleton services, guards, interceptors, global error handling,
  app-wide constants/tokens. No UI components live here.
- `shared/` — reusable, business-logic-free UI (`shared/ui`), directives, pipes,
  models, types, validators. Anything here must work in any future feature.
- `features/<name>/` — one folder per feature module (`pages/`, `components/`,
  `services/`, `models/`, `state/`, `<name>.routes.ts`). Features are lazy-loaded
  and do not import from one another.
- `data/` — API client, feature API services, streaming client, repositories,
  DTOs, mappers. The data layer's own
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

## Communication layer (Sprint 1B)

```
Component → Facade → Repository → Feature API Service → ApiClient → Backend
```

- **ApiClient** (`data/api/api-client.service.ts`) — the only class allowed to
  call `HttpClient`. Generic GET/POST/PUT/PATCH/DELETE with typed headers,
  query params, and an opt-in per-request retry policy.
- **Feature API Services** (`data/api-services/*.service.ts`) — one per feature,
  know endpoint paths and DTO shapes only. `ConversationApiService` is the
  reference implementation; copy its shape for `AuthApiService`,
  `DocumentApiService`, etc. as those features are built.
- **Repositories** (`data/repositories/*.repository.ts`) — decide *where* data
  comes from (REST today; cache/IndexedDB/offline later) and own DTO→domain
  mapping via `data/mappers`. Their public method signatures stay stable
  regardless of the underlying source.
- **Streaming** (`data/streaming/`) — `StreamingClientService` is the reusable
  SSE consumer (fetch + `ReadableStream`, not `EventSource`, so it can send a
  bearer-token `Authorization` header). Returns a cold `Observable<StreamEvent>`;
  unsubscribing aborts the connection automatically. No chat-specific logic —
  built to also serve notifications, agent progress, and background jobs.

### Error handling

`error.interceptor.ts` normalizes every `HttpErrorResponse` into the single
`ApiError` shape (`shared/models/api-error.model.ts`) via
`core/utils/api-error.util.ts`. Repositories, Facades, and the streaming client
all only ever deal with `ApiError` — never a raw HTTP status code or
`HttpErrorResponse`. `ApiError.kind` (`'unauthorized' | 'validation' | 'server' |
'network' | ...`) is what components/facades branch on.

### Interceptor order

`correlationIdInterceptor → authInterceptor → requestLoggingInterceptor →
errorInterceptor` (registered in `app.config.ts`). Correlation ID is stamped
first so later interceptors (and the normalized `ApiError`) can read it back
via `CORRELATION_ID_CONTEXT`.

### Environment / config

`AppConfig` (`core/config/app-config.model.ts`) now carries `apiBaseUrl`,
`streamingBaseUrl`, `appVersion`, `debugMode`, and a `featureFlags` placeholder
(`streamingEnabled`, `toolCallingEnabled`). All environment-specific values
flow through the `APP_CONFIG` injection token — nothing is hardcoded in
services.



## Authentication (Sprint 1 Phase 3) — the reference feature

Full vertical slice, exercising every layer:

```
LoginPageComponent → AuthFacade → AuthRepository → AuthApiService → ApiClientService → Backend
                                        ↓ (on success)
                                  AuthMapper → AuthSession domain model
                                        ↓
                                  AuthFacade → AuthSessionService (Core) → Shell / Guards / Interceptor
```

- **`features/auth/pages/login.page.ts`** — talks only to `AuthFacade`. Never sees
  a DTO or an `HttpErrorResponse`; reads `facade.error()?.message` and
  `facade.isSubmitting()`.
- **`features/auth/services/auth.facade.ts`** — the only thing components inject.
  Owns post-login navigation (`/dashboard`) and post-logout navigation
  (`/auth/login`), and pushes the result into `AuthSessionService` — it's the
  seam between the data layer and Core session state.
- **`features/auth/state/auth-state.service.ts`** — holds only `isSubmitting` and
  `error`. Deliberately does **not** duplicate `isAuthenticated`/`currentUser` —
  those stay single-sourced in Core's `AuthSessionService` and are proxied
  through the Facade unchanged, so there's never a moment where feature state
  and session state could disagree.
- **`data/repositories/auth.repository.ts`** — independent of the auth
  *implementation*: `login()` returns an `AuthSession` regardless of whether
  that came from REST (today), OAuth2/OIDC, Azure AD, Okta, or Auth0 (later).
  Adding a provider later means adding a new method, not changing this one.
- **`data/api-services/auth-api.service.ts`** — `login`, `logout`, plus
  `getCurrentUser()` and `refreshSession()` as *unused-today* placeholders so
  session-restore-on-reload and token refresh are additive later.
- **`core/services/auth-session.service.ts`** — single source of truth for "who
  is logged in," read by the Shell (`UserMenuComponent`), both route guards, and
  the auth interceptor. Now persists the user (not just the token) across a
  page reload, plus an unused `expiresAt`/`isSessionExpired` placeholder for
  future session-expiration handling.
- **Route guards** — `authGuard` (protected routes → redirect to login) and its
  mirror `guestGuard` (login route → redirect an already-authenticated user to
  the dashboard). Both depend only on Core. `app.routes.ts` applies `authGuard`
  once via `canActivateChild` on the whole protected route group, so every
  current and future feature route under it is covered automatically.
- **Shell integration** — `UserMenuComponent` reads `AuthSessionService` directly
  (Core, always allowed) for the display name/email, but "Sign out" is a
  `routerLink` to `/auth/logout` rather than a call into `AuthFacade`. That
  route triggers `LogoutPageComponent`, which calls the Facade. This is what
  keeps "Shell has zero feature knowledge" true while still giving Shell a
  working sign-out control — only a URL string crosses the boundary, same
  pattern the guards already use.
- **Mock mode** (`features/auth/services/auth.mock.ts`) — exercises both the
  success path and the normalized `ApiError` failure path with one hardcoded
  credential pair (`vivek@enterprise.ai` / `password123`), so the full
  loading/error/success UI is demoable with no backend running.

This is the pattern every future feature (Chat, Documents, Settings, Profile,
Agents) should copy.

## Conversation Workspace (Sprint 1 Phase 4) — the reference for reusable UI

Not the AI Chat implementation — the enterprise workspace AI Chat will later live
inside. No backend, no streaming yet; realistic mock data only.

```
ChatPage (only component that injects ChatFacade)
  └─ ConversationWorkspace (pure layout coordinator, zero Facade knowledge)
      ├─ ConversationSidebar → ConversationItem × N
      ├─ ConversationHeader
      ├─ MessageList → MessageBubble × N
      ├─ PromptComposer          (shared/ui — reusable outside Chat entirely)
      └─ RightPanel
```

- **Container/presentational split, deliberately verbose.** Only `ChatPage`
  injects `ChatFacade`. Everything below receives plain inputs and emits plain
  outputs, prop-drilled through `ConversationWorkspace`. Traded for maximum
  reuse of `MessageBubble`/`PromptComposer` elsewhere later. UI-only placeholder
  actions (copy, regenerate, rename, delete, menu) skip the Facade entirely and
  inject `NotificationService` (Core) directly for a "coming soon" toast — same
  precedent as `HeaderComponent`'s bell icon and the Login page's "Forgot
  password?" link.
- **`shared/ui/prompt-composer/`** — auto-growing textarea, configurable
  Enter-to-send vs Ctrl+Enter-to-send, character counter, permanently-disabled
  attachment/mic buttons. Emits `submit(text: string)` only — no idea Chat, AI,
  or a backend exists. Reusable anywhere an "ask AI" input is needed later.
- **`shared/ui/typing-indicator/`** — generic pending-response indicator, not
  chat-specific; reusable for agent progress or background job status later.
- **The exact streaming seam:** `ChatFacade.sendMessage()` appends a user
  message, then appends a placeholder assistant message with
  `status: 'streaming'` and empty content, waits ~900ms via `timer(...)`, then
  fills that same message's `content` in place. That update-in-place pattern is
  structurally identical to what `StreamingClientService.connect()` will do —
  swapping the `timer(...).subscribe(...)` body for a real stream subscription
  is the entire integration; `MessageBubble` never changes.
- **`features/chat/models/`** — `ChatConversationSummary` and `ChatMessage` are
  deliberately NOT shared with `features/conversations`' `Conversation` model,
  even though they'll likely converge once a real conversation-history endpoint
  exists. Flagged here rather than silently forced together — premature
  coupling between two features that don't share a data shape yet.
- **Right panel** (Citations, Sources, Metadata, Execution Timeline, Agent
  Progress) is five static placeholder cards today. Wiring one to real data
  later is additive — the panel's collapse/responsive behavior doesn't change.
- **Responsive:** desktop shows all three columns; the right panel becomes an
  overlay on tablet and hides below `$bp-mobile`; the conversation sidebar
  becomes a fixed-position drawer below `$bp-mobile`, mirroring the Shell's own
  sidebar pattern in `styles/layout/_sidebar.scss`.

## Theming

Light theme is fully implemented via CSS custom properties
(`styles/themes/_light.scss`) driven by design tokens. Dark theme
(`styles/themes/_dark.scss`) and `ThemeService` are architecturally wired
(`data-theme` attribute toggle) but intentionally left unpolished per scope.

## What's real vs. scaffolded in this sprint

**Fully implemented:** shell (sidebar/header/breadcrumbs/user menu, now session-aware),
all three layouts, routing (with route guards wired), SCSS/design-token system,
shared UI kit, Dashboard, Authentication (complete vertical slice — login, logout,
guards, session persistence, now calling the real backend), Conversations history
(full Component→Facade→Repository chain with mock data), AI Chat workspace
(complete three-panel UX — sidebar, header, messages, composer, right panel —
with realistic mock data; no AI/streaming integration yet).

**Scaffolded placeholders** (route + page exist, ready for real implementation):
Documents, Settings, Profile. Wiring up their real UI is a matter of following
the Auth, Conversations, or Chat pattern — no architectural changes needed.
