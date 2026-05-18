# UI Layer — Flutter

Platform-specific UI layer patterns. Canonical definitions: `reference/code-architecture/ui-theory.md`.

---

## Dependency Rule <!-- 9 -->

UI depends on Presentation only — never imports Domain or Data directly.

Allowed imports: `Bloc`/`Cubit` types, `State`/`Event` types, `flutter/material.dart` and other Flutter framework primitives.
Forbidden: use case interfaces, repository interfaces, DTOs, mappers, datasources.

---

## Screen <!-- 16 -->

A **Screen** is a `Widget` (`StatelessWidget` or `StatefulWidget`) bound to a single `Bloc`/`Cubit`. It observes state via `BlocBuilder`/`BlocListener` and dispatches events — it contains no business logic.

**Invariants:**
- Wrapped with `BlocProvider` that resolves the Bloc from `GetIt` or a feature-scoped DI accessor (e.g. `[feature]Dependency<MyBloc>()`) — never `MyBloc()` inline
- `StatefulWidget` is used when screen lifecycle (`initState`, `dispose`) is needed — e.g. to trigger the initial Bloc event on mount
- Observes every `State` variant via `BlocBuilder` — no state variant goes unhandled
- Sends events via `context.read<MyBloc>().add(...)` for every user interaction — never mutates state directly
- Contains no business logic — `if`/`switch` only decides what to render
- No use case calls — all data flows through the Bloc

**When to create:** One Screen widget per route. Created after the Bloc/Cubit contract exists.

---

## Component / Sub-view <!-- 14 -->

A **Component** is a reusable `StatelessWidget` smaller than a full screen.

**Invariants:**
- Stateless by default — receives data via constructor parameters and emits callbacks via `VoidCallback`/typed callbacks
- If stateful, wrapped with a scoped `BlocProvider` — never manages business state inline
- No use case calls — all data passed in from the parent Screen or a scoped Bloc
- Reuse check required before creating — search `presentation/common/widgets/` and shared packages first

**When to create:** When a UI element appears in ≥2 screens, or when a Screen section is complex enough to isolate for readability.

---

## Navigator / Coordinator <!-- 14 -->

A **Navigator** is GoRouter's `AppRouter` singleton that owns all navigation logic for the app or feature.

**Invariants:**
- The Screen delegates navigation intent via `BlocListener` — it never hard-codes a destination in a button handler
- The Bloc emits a `NavAction` field in `State` — the Screen's `BlocListener` calls `context.go/push`
- Route constants defined in `Routes` class — the Screen never constructs path strings inline
- One `AppRouter` per app (or per module in modular setups) — not per screen

**When to create:** When a Screen navigates to another screen. `Routes` constants and `AppRouter` created before the Screen that triggers navigation. See `navigation-impl.md` for full GoRouter pattern.

---

## DI Wiring <!-- 13 -->

**DI wiring** registers the `Bloc`/`Cubit` in the `GetIt` container via `injectable`.

**Invariants:**
- Bloc annotated `@injectable` (or `@lazySingleton` for shared state) — scope matches feature lifetime
- Use cases injected into the Bloc constructor — never instantiated inside the Bloc
- `BlocProvider` in Screen resolves via `getIt<MyBloc>()` or a feature-scoped accessor `[feature]Dependency<MyBloc>()` — never constructed inline

**When to create:** After the Screen and Bloc exist. Required before the route is reachable.

---

## Creation Order <!-- 10 -->

```
Screen widget → AppRouter route entry + Routes constant (if navigation needed) → GetIt registration
```

The `Bloc`/`Cubit` and its contract must exist before any UI layer file is written.

---

## Layer Invariants <!-- 10 -->

- Screen never mutates state directly — observes via `BlocBuilder`/`BlocConsumer` only
- Screen never calls use cases directly — all interactions dispatched as Bloc events
- Bloc instantiated via GetIt — never `MyBloc()` inline in a widget tree
- Navigation delegated to GoRouter via `BlocListener` — Screen emits nav action, not destination
- No data layer knowledge — no DTOs, no datasources, no HTTP types visible in widget files

---

## Planner Search Patterns <!-- 7 -->

When exploring the UI layer, glob for:
- `**/presentation/screens/**/*_screen.dart` — screen files
- `**/presentation/common/widgets/**/*.dart` — shared component files
- `**/presentation/navigation/app_router.dart` — router configuration
- `**/presentation/navigation/routes.dart` — route constants
