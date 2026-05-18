# Flutter Qontak — Module Structure

> Project layout and module types: `reference/project.md`.
> This file covers Dart code patterns for creating and wiring modules.

> **Architecture note:** `mobile-qontak-chat` uses a **centralized route manager** (`lib/route_manager.dart`) and manual `GetIt` registration rather than per-module `BaseModule.routes()` / `@InjectableInit`. The `BaseModule` pattern below is the target architecture for future new feature modules added to the app layer.

---

## BaseModule Contract <!-- 24 -->

`BaseModule` lives in `[prefix]_core` and defines what the Application module
needs from every feature module:

```dart
// [prefix]_core/lib/src/base/base_module.dart
import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';

abstract class BaseModule {
  List<RouteBase> routes();
  LocalizationsDelegate<dynamic>? localizationsDelegate();
  List<CollectionSchema> collectionSchemas(); // or List<Type> if using another DB
}
```

**Rules:**
- Every feature module implements `BaseModule` exactly once, in `src/configs/`.
- Return `null` from `localizationsDelegate()` if the module has no translations.
- Return `[]` from `collectionSchemas()` if the module has no local DB tables.

---

## Feature Module — BaseModule Implementation <!-- 30 -->

```dart
// features/[prefix]_auth/lib/src/configs/auth_module.dart
import 'package:go_router/go_router.dart';
import 'package:[prefix]_core/[prefix]_core.dart';
import '../presentation/screens/login_screen.dart';
import '../gen/l10n/auth_localizations.dart';

class AuthModule implements BaseModule {
  @override
  List<RouteBase> routes() => [
        GoRoute(
          path: '/login',
          name: 'login',
          builder: (context, state) => const LoginScreen(),
        ),
      ];

  @override
  LocalizationsDelegate<dynamic>? localizationsDelegate() =>
      AuthLocalizations.delegate;

  @override
  List<CollectionSchema> collectionSchemas() => [];
}
```

---

## ModuleRegistrar (Application Module) <!-- 49 -->

`ModuleRegistrar` aggregates all `BaseModule` implementations so the app's
`main.dart` / runner has a single registration call:

```dart
// lib/configs/di/module_registrar.dart
import 'package:[prefix]_auth/[prefix]_auth.dart';
import 'package:[prefix]_inbox/[prefix]_inbox.dart';

class ModuleRegistrar {
  static final List<BaseModule> _modules = [
    AuthModule(),
    InboxModule(),
    // register new modules here
  ];

  static List<RouteBase> get routes =>
      _modules.expand((m) => m.routes()).toList();

  static List<LocalizationsDelegate<dynamic>> get localizationDelegates =>
      _modules
          .map((m) => m.localizationsDelegate())
          .whereType<LocalizationsDelegate<dynamic>>()
          .toList();

  static List<CollectionSchema> get collectionSchemas =>
      _modules.expand((m) => m.collectionSchemas()).toList();
}
```

```dart
// lib/src/runner.dart
void runApplication() {
  runApp(
    MaterialApp.router(
      routerConfig: GoRouter(routes: ModuleRegistrar.routes),
      localizationsDelegates: [
        ...ModuleRegistrar.localizationDelegates,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ],
    ),
  );
}
```

---

## Shared Module — Core Setup <!-- 13 -->

```dart
// shared/[prefix]_core/lib/[prefix]_core.dart
// Export only the public API surface
export 'src/base/base_module.dart';
export 'src/base/use_case.dart';
export 'src/network/api_client.dart';
export 'src/module_api/auth_module_api.dart'; // add as features define APIs
```

---

## Dependencies Module <!-- 29 -->

The dependencies module installs shared packages and re-exports them so
feature modules avoid version conflicts:

```yaml
# shared/[prefix]_dependencies/pubspec.yaml
dependencies:
  flutter_bloc: ^8.1.6
  freezed_annotation: ^2.4.4
  json_annotation: ^4.9.0
  get_it: ^8.0.2
  injectable: ^2.4.4
  go_router: ^14.0.0
  dio: ^5.7.0
  logger: ^2.4.0
```

```dart
// shared/[prefix]_dependencies/lib/[prefix]_dependencies.dart
export 'package:flutter_bloc/flutter_bloc.dart';
export 'package:freezed_annotation/freezed_annotation.dart';
export 'package:get_it/get_it.dart';
export 'package:go_router/go_router.dart';
// export all others...
```

Feature modules declare only `[prefix]_dependencies` as a dependency —
never individual packages that it already re-exports.
