# Flutter — App Layer

> Concepts and invariants: `reference/code-architecture/app-layer-theory.md`. This file covers Dart/get_it patterns for Flutter.

## Dependency Registration <!-- 56 -->

Flutter uses **get_it** as the service locator with **injectable** code generation per feature.

**Step 1 — Create the feature DI file:**

```dart
// talenta/lib/src/features/{feature}/configs/di/{feature}_dependencies.dart

import 'package:injectable/injectable.dart';
import 'package:get_it/get_it.dart';

@module
abstract class {Feature}Dependencies {
  @lazySingleton
  {Feature}Repository get{Feature}Repository(
    {Feature}RemoteDataSource remoteDataSource,
  ) =>
      {Feature}RepositoryImpl(remoteDataSource: remoteDataSource);

  @lazySingleton
  {Feature}RemoteDataSource get{Feature}RemoteDataSource(
    ApiClient apiClient,
  ) =>
      {Feature}RemoteDataSourceImpl(apiClient: apiClient);

  @lazySingleton
  Get{Feature}ListUseCase get{Feature}ListUseCase(
    {Feature}Repository repository,
  ) =>
      Get{Feature}ListUseCase(repository: repository);
}
```

**Step 2 — Register the DI module in `talenta_dependencies.dart`:**

```dart
// lib/src/configs/di/talenta_dependencies.dart

// Add the import:
import 'package:talenta/src/features/{feature}/configs/di/{feature}_dependencies.dart';

// The @module class is picked up automatically by build_runner — no manual registration needed.
// Run:
// flutter pub run build_runner build --delete-conflicting-outputs
```

**Rules:**
- ✅ One `@module` abstract class per feature under `configs/di/`
- ✅ Use `@lazySingleton` for repositories, data sources, and use cases
- ✅ Use `@injectable` on BLoC classes (BLoCs are never singletons — new instance per page)
- ✅ Run `build_runner` after any DI change to regenerate `*.g.dart` files
- ❌ Never call `GetIt.instance.registerSingleton(...)` manually — always use annotations

---

## Route Registration <!-- 55 -->

Flutter features declare routes via a **route constants file** and a **route factory class**.

**Step 1 — Create the route constants:**

```dart
// talenta/lib/src/features/{feature}/utils/navigation/{feature}_route.dart

abstract class {Feature}Route {
  static const String root = '/{feature}';
  static const String detail = '/{feature}/detail';
}
```

**Step 2 — Create the route factory:**

```dart
// talenta/lib/src/features/{feature}/utils/navigation/{feature}_route_factory.dart

import 'package:flutter/widgets.dart';

class {Feature}RouteFactory {
  static Widget? getPageByName(String name, {Map<String, dynamic>? args}) {
    switch (name) {
      case {Feature}Route.root:
        return {Feature}Page();
      case {Feature}Route.detail:
        return {Feature}DetailPage(id: args?['id'] as String? ?? '');
      default:
        return null;
    }
  }

  static List<RouteProvider>? getListProviderByName(String name) {
    switch (name) {
      case {Feature}Route.root:
        return [{Feature}BlocProvider()];
      default:
        return null;
    }
  }
}
```

**Step 3 — Register the factory in the module (handled in Module Registration below).**

**Rules:**
- ✅ Route constants are plain `abstract class` with `static const String` — no logic
- ✅ `getPageByName` returns `null` for unknown routes — caller falls through to next factory
- ✅ `getListProviderByName` returns BLoC providers needed by the page
- ❌ No `Navigator.push` calls inside route factories — factories are page builders only

---

## Module Registration <!-- 51 -->

Flutter uses **BaseModule** + **TalentaModuleManager** for explicit feature module registration.

**Step 1 — Create the feature module:**

```dart
// talenta/lib/src/features/{feature}/{feature}.dart

import 'package:talenta_core/talenta_core.dart';

class {Feature}Module extends BaseModule {
  @override
  String get name => '{feature}';

  @override
  Widget? getPageByName(String name, {Map<String, dynamic>? args}) =>
      {Feature}RouteFactory.getPageByName(name, args: args);

  @override
  List<RouteProvider>? getListProviderByName(String name) =>
      {Feature}RouteFactory.getListProviderByName(name);
}
```

**Step 2 — Register in TalentaModuleManager:**

```dart
// talenta/lib/src/shared/core/module/module_manager.dart

import 'package:talenta/src/features/{feature}/{feature}.dart';

class TalentaModuleManager {
  static final List<BaseModule> _modules = [
    // ... existing modules
    {Feature}Module(),  // ← add here
  ];

  // existing registration logic...
}
```

**Rules:**
- ✅ One `BaseModule` subclass per feature
- ✅ `name` must be unique across all modules — use the feature's snake_case identifier
- ✅ Module delegates all routing to `{Feature}RouteFactory` — no inline page construction
- ✅ Register in `TalentaModuleManager._modules` list — never elsewhere
- ❌ No lifecycle logic in the module — `onStart`/`onStop` hooks are not used in Talenta's BaseModule

---

## Analytics Constants <!-- 16 -->

Analytics event names and screen identifiers are declared as constants in the feature's `utils/` or a dedicated `constants/` file — never as inline strings in BLoC/ViewModel code.

**Path pattern:** `talenta/lib/src/features/{feature}/utils/{feature}_analytics.dart` or `constants/{feature}_analytics_constants.dart`

**Rules:**
- ✅ One constants class/file per feature
- ✅ Plain `static const String` values — no logic, no analytics SDK import
- ✅ snake_case string values matching the analytics platform convention
- ❌ Never inline event name strings in BLoC or UI layer code

**When to create:** Any feature that instruments user interactions or screen views. Optional — skip if the feature has no analytics events.

---

## Feature Flag Registration <!-- 16 -->

Discover the feature flag pattern in use for this project — Flutter projects vary. Common patterns:

- **`mekari_flag` / remote config wrapper** — a constants class with flag key strings + a service/repository that resolves them
- **`FeatureFlagRepository`** — a shared repository with one method per flag, returning `bool`

Grep for existing flag registrations before proposing a new one:
```
Grep "featureFlag\|FeatureFlag\|feature_flag" in lib/src/
```

**When to add:** Any feature that requires remote gating or gradual rollout. Optional — skip for features that launch to 100% of users immediately.

---

## Planner Search Patterns <!-- 15 -->

Consumed by `builder-app-planner`. `{Feature}` = PascalCase, `{feature}` = snake_case per Dart convention.

| Scope key | Glob / Path | Grep hint |
|---|---|---|
| `di` | `*{feature}_dependencies.dart`, `*talenta_dependencies.dart`, `*configs/di*` | feature name in `lib/src/configs/di/talenta_dependencies.dart` |
| `route` | `*{feature}_route.dart`, `*{feature}_route_factory.dart` | — |
| `module` | `*module_manager.dart`, `{feature}.dart` in feature root | `TalentaModuleManager` or `BaseModule` |
| `analytics` | `*{feature}_analytics*.dart`, `*{feature}*analytics_constants.dart` under `utils/` or `constants/` | — |
| `feature_flag` | grep only — no fixed path | `featureFlag\|FeatureFlag\|feature_flag` in `lib/src/` |
| `hybrid_embedding` | `talenta/lib/src/brick/*`, `brick_constants.dart` | `## Hybrid Embedding` section below |

---

## Push Notification Registration <!-- 6 -->

> No convention established yet. Document the Flutter FCM token lifecycle and notification handler wiring pattern here when adopted.

---

## Deeplink Registration <!-- 6 -->

> No convention established yet. Document the Flutter deeplink handling pattern (go_router, app_links, or equivalent) here when adopted.

---

## Hybrid Embedding <!-- 93 -->

> Canonical terms and invariants: `reference/code-architecture/app-layer-theory.md` — `## Hybrid Embedding` section.
> This section covers the Flutter guest side — how the Dart module receives host context and calls back to native.

### Key Files <!-- 15 -->

| File | Role |
|------|------|
| `talenta/lib/src/brick/brick_module.dart` | `TalentaModule` — `BrickModule` impl, declares routes and DI bindings |
| `talenta/lib/src/brick/brick_router.dart` | `TalentaModuleRouter` — resolves a `brick://` URI to a `BrickWidget` |
| `talenta/lib/src/brick/brick_executor.dart` | `TalentaModuleExecutor` — headless execution path, returns `ExecutorResponse` |
| `talenta/lib/src/brick/brick_constants.dart` | Module host constant (`moduleHost`) — must match the host's engine config |
| `talenta/lib/src/brick/brick_app.dart` | `BrickApp` — root widget wrapping all guest content |
| `talenta/lib/src/shared/core/module/module_manager.dart` | `TalentaModuleManager` — maps base routes to sub-module handlers |

The `brick_way` package (external dependency) provides `BrickModule`, `BrickRouter`, `BrickExecutor`, `BrickWidget`, `Bricks`, and MethodChannel plumbing — the guest never calls `MethodChannel` directly.

### Guest → Host: Response / Action <!-- 23 -->

The guest never calls `MethodChannel` directly. All calls go through `brick_way`:

```dart
// Return data to host after a navigation flow completes
BricksChannel.sendResponse(data: {...});

// Return an error to host
BricksChannel.sendResponse(error: {...});

// Request a native action (e.g., open a native screen)
BricksChannel.sendActionRequest(
  actionName: 'openPage',
  actionData: {'page': {'ios': 'NativeClassName', 'android': 'co.talenta.NativeActivity'}},
);
```

The host `BricksChannelDelegate` (iOS) / `BrickChannelDelegate` (Android) receives these via `setMethodCallHandler`.
On Android, `sendActionRequest` is routed to the registered `BrickActionListener`. On iOS, it is handled inline in `BricksChannelDelegate`.

### Receiving HostParams <!-- 37 -->

HostParams arrive as the `hostParam` query argument in the URI. `BrickRouter.getTarget()` and `BrickExecutor.execute()` both parse them via:

```dart
final argument = getArgument(uri)['hostParam'] ?? '';
final Map<String, dynamic> hostJson = json.decode(argument); // synchronous — not a Future

// Standard keys (all platforms)
final authJson    = hostJson[Constants.authenticationJson]; // token, refreshToken, locale, isUseKong
final userJson    = hostJson[Constants.userJson];           // user profile
final toggleJson  = hostJson[Constants.toggleJson];         // feature toggles
final flagJson    = hostJson[Constants.featureFlagJson];    // remote config flags

// Android-only top-level config keys (passed via Bricks.initialize() global config, not hostParam)
// app_version, build_number    — from BrickHelper.getFlutterAppProperty()
// device_id, device_model,
// os_version, device_fingerprint — from BrickHelper.getFlutterDeviceProperty()
```

After decoding, call `ExternalDataSourceHelper.initializeConfig()` to seed the decoded blobs into in-memory config — this is required before rendering any feature screen:

```dart
await ExternalDataSourceHelper.initializeConfig(
  externalDataSource: ...,
  prefHelper: ...,
  userJson: userJson,
  toggleJson: toggleJson,
  authenticationJson: authJson,
  featureFlagJson: flagJson,
  hostType: hostType,
  mekariLogManager: ...,
);
```

### Adding a New Guest Module <!-- 11 -->

1. **Create a sub-module** under the relevant module directory with its own routes, BLoC, and DI
2. **Register routes** in the module manager's route resolver (`getResolvingModule(baseRoute)`) — map the base route string to the sub-module handler
3. **Add DI init** in the module manager's initialization method (`initializeModuleDependencies()`) if the sub-module has its own DI
4. **Declare routes** in `TalentaModule.routes` getter — this is consumed by the guest's `BrickRouter` to determine which URIs this module handles; it is **not** read by the host
5. **Seed HostParams** — ensure both `BrickRouter.getTarget()` and `BrickExecutor.execute()` call `ExternalDataSourceHelper.initializeConfig()` (or equivalent) before invoking the sub-module
6. **Coordinate with host team** — agree on the `moduleHost` value in `brick_constants.dart` and the engine slot ID string; these must match the host's `<Name>Config.engineId` / `ENGINE_ID` exactly

### MethodChannel Constants <!-- 10 -->

```
Channel name:      com.mekari.module
open               host → guest: render URI as full-screen page
execute            host → guest: run URI headlessly
sendResponse       guest → host: return data or error (routed to ResponseHandler)
sendActionRequest  guest → host: request native action (routed to ActionListener on Android, inline on iOS)
is24HourFormat     guest → host: query device locale format (sync reply)
```
