# UI Layer — Flutter Qontak

Platform-specific UI layer patterns. Canonical definitions: `reference/code-architecture/ui-theory.md`.

---

## Dependency Rule <!-- 9 -->

UI depends on Presentation only — never imports Domain or Data directly.

Allowed imports: `Bloc`/`Cubit` types, `State`/`Event` types, `[prefix]_core` shared primitives, `flutter/material.dart`.
Forbidden: use case interfaces, repository interfaces, DTOs, mappers, datasources, or direct imports from another feature module.

---

## Screen <!-- 20 -->

A **Screen** is a `StatelessWidget` or `StatefulWidget` that observes state via `BlocBuilder`/`BlocListener`/`BlocConsumer` and dispatches events — it contains no business logic.

**Invariants:**
- `BlocProvider` placed at the route manager (`route_manager.dart` inside a `case` block) — not inside the Screen widget itself
- For app-wide BLoCs (e.g. `UserProfileBloc`, `NotificationBloc`): wired in `provider.dart` (`AppProvider`) instead
- Resolved via typed accessor functions (`mainDependency()`, `coreDependency()`) — never `MyBloc()` inline
- Observes state via `BlocBuilder`/`BlocConsumer` with `buildWhen` to avoid unnecessary rebuilds
- Sends events via `context.read<MyBloc>().add(...)` — never mutates state directly
- Contains no business logic — `if`/`switch` only decides what to render
- Status checks use `.status.isHasData`, `.status.isError`, `.status.isLoading` (NOT `.isLoaded`, `.hasError`)

**When to create:** One Screen widget per route. Created after the Bloc contract exists. `BlocProvider` wiring added in the relevant `case` block of `route_manager.dart`.

---

## BlocProvider.value (Route-Scoped BLoC Reuse) <!-- 18 -->

When a route needs to use a BLoC instance that already exists higher in the widget tree (e.g. a calling BLoC created at the initiating screen and passed into a sub-route), use `BlocProvider.value` instead of `BlocProvider`. This passes the existing instance without recreating or closing it.

```dart
// lib/route_manager.dart
case QontakAppRoute.calling:
  final args = settings.arguments as CallingArgs;
  return MaterialPageRoute(
    builder: (_) => BlocProvider.value(
      value: args.callingBloc, // existing instance passed via route args
      child: const CallingPage(),
    ),
  );
```

```dart
// Navigating to the route — pass the BLoC in args
Navigator.of(context).pushNamed(
  QontakAppRoute.calling,
  arguments: CallingArgs(callingBloc: context.read<CallingBloc>()),
);
```

**Invariants:**
- Use `BlocProvider.value` when the BLoC lifecycle must outlive the destination route (e.g. an active call BLoC that was already created)
- Use `BlocProvider` (with `create:`) for all other route entries — new instance scoped to the route
- `BlocProvider.value` does **not** close the BLoC when the route is popped — the owner (the caller) is responsible for closing it
- Never pass a `BuildContext` through route arguments — pass typed BLoC instances or plain value objects only

**When to use:** Long-lived BLoCs that span multiple routes (e.g. active call, ongoing upload, multi-step wizard) where the sub-route must share state with the originating screen.

---

## Component / Sub-view <!-- 14 -->

A **Component** is a reusable `StatelessWidget` smaller than a full screen, living in `[prefix]_core` if shared across modules.

**Invariants:**
- Stateless by default — receives data via constructor parameters and emits callbacks via typed callbacks
- If stateful, wrapped with a scoped `BlocProvider` — never manages business state inline
- No use case calls — all data passed in from the parent Screen or a scoped Bloc
- Reuse check required before creating — search `[prefix]_core/lib/src/widgets/` and `[prefix]_core/lib/src/components/` first

**When to create:** When a UI element appears in ≥2 modules, or when a Screen section is complex enough to isolate. Cross-module components live in `[prefix]_core`.

---

## Navigator / Coordinator <!-- 14 -->

Navigation uses `Navigator` 1.0 + `NavigationHelper.pushNamed` (not `go_router`). Routes are centralized in `route_manager.dart`.

**Invariants:**
- The Screen delegates navigation intent via `BlocListener` — never hard-codes a destination inline
- The BLoC transitions state (e.g. `loginState.status.isHasData`) — the `BlocListener` calls `Navigator.of(context).pushReplacementNamed()`
- Route name constants in `QontakAppRoute` — a single abstract class in `lib/config/constants/`
- Cross-package navigation (e.g. from notification handler) uses `NavigationHelper.pushNamed()` with the global `navigatorKey`

**When to create:** When a Screen navigates to another screen. Route entry added to `route_manager.dart`. See `navigation-impl.md` for the full centralized navigation pattern.

---

## DI Wiring <!-- 14 -->

**DI wiring** registers the `Bloc` in `MainDependency._registerPresentation()` using `registerFactory`.

**Invariants:**
- BLoC registered with `registerFactory` (new instance per call) — never `registerLazySingleton`
- Use cases injected into the BLoC constructor via named parameters — never instantiated inside the BLoC
- App-level BLoC registration lives in `MainDependency.registerMain()` in `lib/config/di/main_dependency.dart`
- No `@injectable` annotations in the app module — all DI is manual GetIt calls

**When to create:** After the Screen and BLoC exist. `registerFactory` call added to `_registerPresentation()` in `MainDependency`, then `BlocProvider` added to the relevant `case` in `route_manager.dart` (or to `AppProvider` for global BLoCs).

---

## Creation Order <!-- 10 -->

```
Screen widget → BaseModule.routes() entry + [ModulePrefix]Routes constant (if navigation needed) → module DI registration
```

The `Bloc`/`Cubit` and its contract must exist before any UI layer file is written.

---

## Layer Invariants <!-- 10 -->

- Screen never mutates state directly — observes via `BlocBuilder`/`BlocConsumer` only
- Screen never calls use cases directly — all interactions dispatched as Bloc events
- Bloc instantiated via GetIt — never `MyBloc()` inline in a widget tree
- Navigation delegated via `BlocListener` + Module API — no direct imports between feature modules
- No data layer knowledge — no DTOs, no datasources, no HTTP types visible in widget files

---

## Planner Search Patterns <!-- 8 -->

When exploring the UI layer, glob for:
- `**/lib/src/presentation/screens/**/*_screen.dart` — screen files within a module
- `**/[prefix]_core/lib/src/widgets/**/*.dart` — shared component files
- `**/[prefix]_core/lib/src/components/**/*.dart` — shared component files (alternate path)
- `**/lib/src/configs/*_module.dart` — module route registration files
- `**/lib/src/configs/*_routes.dart` — per-module route constants
