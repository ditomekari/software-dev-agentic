# Flutter Qontak — Dependency Injection

> Single-package DI patterns: `../../flutter/reference/code-architecture/di-impl.md`.
> This file covers app-level DI orchestration and per-module manual `GetIt` registration.

No code generation (`@InjectableInit`, `injectable_generator`) is used in the app module. All DI is manual static methods with `GetIt`.

---

## DI Architecture <!-- 18 -->

The app module is the DI root. External feature packages each expose a static `register*()` method. The app calls them in dependency order via `ChatDi.initDependency()`.

```
engine.dart
  └── ChatDi.initDependency()
        ├── CoreDependency.registerCore()          ← chat_core (networking, logger, prefs)
        ├── ContactDependency.registerContact()    ← chat_contact
        ├── ComposerDependency.registerComposer()  ← chat_composer
        ├── MessagingDependency.registerMessaging() ← chat_messaging
        ├── InboxDependency.registerInbox()        ← chat_inbox
        ├── ConversationDependency.registerConversation() ← chat_conversation
        ├── CallDependency.registerCall()          ← chat_call
        ├── MainDependency.registerMain()          ← app-level (depends on all above)
        └── ChatNotificationDependency.registerChatNotification()
```

---

## Module DI Accessors <!-- 14 -->

Each feature package exposes a typed accessor function (from `chat_core`/`chat_dependency`). These are the preferred way to resolve dependencies from feature packages:

```dart
// Resolving dependencies from feature packages
coreDependency<NavigationHelper>()       // chat_core
inboxDependency<GetRoomByIdUseCase>()    // chat_inbox
messagingDependency<GetMessageByIdUseCase>() // chat_messaging
contactDependency<ContactRemoteDataSource>() // chat_contact
composerDependency<UploadFollowUpMediaUseCase>() // chat_composer
callDependency<BaseNativeChannel>()      // chat_call
mainDependency<GetFirstRunUseCase>()     // app-level (GetIt.instance)
```

---

## App-Level Registration (`MainDependency`) <!-- 30 -->

App-level dependencies follow a `_registerData → _registerDomain → _registerPresentation` pattern:

```dart
// lib/config/di/main_dependency.dart
final mainDependency = GetIt.instance;

class MainDependency {
  static void registerMain() {
    _registerData();
    _registerDomain();
    _registerPresentation();
  }

  static void _registerData() {
    mainDependency.registerLazySingleton<ProductTourLocalDataSource>(
      () => ProductTourLocalDataSourceImpl(preferences: coreDependency()),
    );
  }

  static void _registerDomain() {
    mainDependency
      ..registerLazySingleton(() => GetFirstRunUseCase(repository: mainDependency()))
      ..registerLazySingleton(() => SetFirstRunUseCase(repository: mainDependency()))
      ..registerLazySingleton<ProductTourRepository>(
        () => ProductTourRepositoryImpl(localDataSource: mainDependency()),
      );
  }

  static void _registerPresentation() {
    mainDependency
      ..registerFactory(() => BottomNavigationBloc(
            getUnreadRoomCount: mainDependency(),
            subscribeMessageUseCase: mainDependency(),
            subscribeMarkMessagesAsReadUseCase: mainDependency(),
          ))
      ..registerFactory(() => NotificationTrayBloc(
            getInitialMessageUseCase: mainDependency(),
            qontakMonitor: mainDependency(),
          ));
  }
}
```

---

## Scope Rules <!-- 13 -->

| GetIt method | Scope | Use for |
|---|---|---|
| `registerLazySingleton` | Singleton, created on first access | DataSources, Repositories, Use Cases, Services |
| `registerSingleton` | Singleton, created eagerly at registration | Services requiring immediate init |
| `registerFactory` | New instance per call | BLoCs, Cubits — stateful, one per screen |
| `registerLazySingleton<IFace>(() => Impl())` | Singleton under abstract type | Repository and DataSource implementations |

**Never use `registerLazySingleton` for BLoCs** — BLoC holds mutable state; `BlocProvider` must get a fresh instance via `registerFactory`.

---

## Registration Order Rules <!-- 9 -->

1. `CoreDependency.registerCore()` — networking, logger, prefs, base services
2. Feature package `register*()` calls — each in its own step
3. `MainDependency.registerMain()` — app-level; depends on feature packages being registered
4. `ChatNotificationDependency` — last, depends on messaging + core

---

## Resolving in BlocProvider (Route-Scoped) <!-- 16 -->

BLoCs resolved at route time use the appropriate accessor function directly in `route_manager.dart`:

```dart
// lib/route_manager.dart
case QontakAppRoute.login:
  return BlocProvider(
    create: (_) => LoginBloc(
      getSSOTokenUseCase: mainDependency(),    // ← resolved from GetIt.instance
      prefHelper: coreDependency(),            // ← resolved from chat_core
    ),
    child: const LoginScreen(),
  );

// Multi-provider route
case QontakAppRoute.contactDetail:
  return MultiBlocProvider(
    providers: [
      BlocProvider(
        create: (_) => DetailContactBloc(
          getContactByIdUseCase: contactDependency(),
          qontakMonitor: coreDependency(),
          offlineMode: coreDependency(),
          // ...
        ),
      ),
      BlocProvider(create: (_) => messagingDependency<GetRoomBloc>()),
    ],
    child: ContactDetailScreen(arguments: arguments! as ContactDetailArguments, ...),
  );
```

---

## Global Provider Wiring <!-- 10 -->

App-wide BLoCs (not scoped to a single route) are wired in `provider.dart` (`AppProvider`) — see `app-layer-impl.md`. They are resolved in the same way, using typed accessor functions.

---

## Testing with DI <!-- 14 -->

Prefer constructor injection — pass mock instances directly, no `getIt` manipulation:

```dart
setUp(() {
  mockGetFirstRunUseCase = MockGetFirstRunUseCase();
  bloc = ProductTourBloc(
    mockGetFirstRunUseCase,
    mockSetFirstRunUseCase,
    mockGetQuestStatusUseCase,
    mockSetQuestStatusUseCase,
  );
});
```

When a test must interact with the global `GetIt.instance`, reset it in `tearDown`:

```dart
tearDown(() => GetIt.instance.reset());
```
