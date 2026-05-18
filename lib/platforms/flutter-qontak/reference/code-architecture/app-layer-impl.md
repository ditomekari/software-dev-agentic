# Flutter Qontak — App Layer

> Concepts and invariants: `lib/core/reference/code-architecture/app-layer-theory.md`. This file covers Dart patterns for the application module.

The application module is the entry point. It owns: `main.dart`, runner, DI aggregation, routing, and entry-point screens (splash, onboarding, main nav shell). Feature code belongs in feature packages.

---

## main.dart <!-- 17 -->

```dart
// lib/main.dart
import 'package:flutter/widgets.dart';
import 'configs/di/injection.dart';
import 'src/runner.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDependencies();
  runApplication();
}
```

---

## Runner <!-- 27 -->

```dart
// lib/src/runner.dart
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import '../configs/di/module_registrar.dart';

void runApplication() {
  runApp(
    MaterialApp.router(
      routerConfig: ModuleRegistrar.router,
      localizationsDelegates: [
        ...ModuleRegistrar.localizationDelegates,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('id')],
      theme: AppTheme.light,
    ),
  );
}
```

---

## DI Aggregation <!-- 39 -->

```dart
// lib/configs/di/injection.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

// Feature module DI initializers
import 'package:[prefix]_auth/src/configs/auth_di.dart';
import 'package:[prefix]_inbox/src/configs/inbox_di.dart';
import 'package:[prefix]_messaging/src/configs/messaging_di.dart';

import 'injection.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async {
  // Core first
  await initCoreDependencies();         // from [prefix]_core

  // Feature modules
  await initAuthDependencies();
  await initInboxDependencies();
  await initMessagingDependencies();
  // add new modules here

  // App-level config
  await getIt.init();
}
```

**Rules:**
- Core always initializes before feature modules
- Feature modules initialize before app-level
- Never call `GetIt.instance.registerSingleton(...)` manually — use annotations

---

## ModuleRegistrar <!-- 43 -->

```dart
// lib/configs/di/module_registrar.dart
import 'package:go_router/go_router.dart';
import 'package:[prefix]_core/[prefix]_core.dart';
import 'package:[prefix]_auth/[prefix]_auth.dart';
import 'package:[prefix]_inbox/[prefix]_inbox.dart';
import 'package:[prefix]_messaging/[prefix]_messaging.dart';

class ModuleRegistrar {
  static final List<BaseModule> _modules = [
    AuthModule(),
    InboxModule(),
    MessagingModule(),
    // register new modules here
  ];

  static GoRouter get router => GoRouter(
        initialLocation: '/',
        redirect: _globalGuard,
        routes: _modules.expand((m) => m.routes()).toList(),
      );

  static List<LocalizationsDelegate<dynamic>> get localizationDelegates =>
      _modules
          .map((m) => m.localizationsDelegate())
          .whereType<LocalizationsDelegate<dynamic>>()
          .toList();

  static List<CollectionSchema> get collectionSchemas =>
      _modules.expand((m) => m.collectionSchemas()).toList();

  static String? _globalGuard(BuildContext context, GoRouterState state) {
    // Resolve AuthNavigationApi from DI for auth guard
    final authApi = getIt<AuthNavigationApi>();
    return authApi.redirectIfUnauthenticated(context, state);
  }
}
```

---

## Route Registration per Module <!-- 41 -->

Each feature module declares its own routes in `BaseModule.routes()`:

```dart
// features/[prefix]_inbox/lib/src/configs/inbox_module.dart
class InboxModule implements BaseModule {
  @override
  List<RouteBase> routes() => [
        GoRoute(
          path: '/inbox',
          name: 'inbox',
          builder: (context, state) => const InboxScreen(),
          routes: [
            GoRoute(
              path: ':conversationId',
              name: 'conversation',
              builder: (context, state) => ConversationScreen(
                conversationId: state.pathParameters['conversationId']!,
              ),
            ),
          ],
        ),
      ];
}
```

Route path and name constants belong in the feature package:

```dart
// features/[prefix]_inbox/lib/src/configs/inbox_routes.dart
abstract class InboxRoutes {
  InboxRoutes._();
  static const String inbox = '/inbox';
  static const String conversation = '/inbox/:conversationId';
  static String conversationPath(String id) => '/inbox/$id';
}
```

---

## Analytics & Error Reporting <!-- 17 -->

```dart
// lib/configs/analytics/analytics_setup.dart
Future<void> initAnalytics() async {
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;
  await FirebaseAnalytics.instance.setAnalyticsCollectionEnabled(
    !kDebugMode,
  );
}
```

Call `initAnalytics()` in `main()` before `configureDependencies()`.

---

## Planner Search Patterns <!-- 8 -->

| Scope key | Path | Grep hint |
|---|---|---|
| `di` | `lib/configs/di/injection.dart`, `lib/configs/di/module_registrar.dart` | `configureDependencies`, `ModuleRegistrar` |
| `route` | `lib/configs/di/module_registrar.dart`, each `*_module.dart` | `BaseModule`, `routes()` |
| `module` | `features/*/lib/src/configs/*_module.dart` | `implements BaseModule` |
| `analytics` | `lib/configs/analytics/` | `FirebaseAnalytics`, `logEvent` |
