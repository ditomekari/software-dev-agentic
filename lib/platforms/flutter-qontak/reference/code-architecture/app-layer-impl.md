# Flutter Qontak — App Layer

> Concepts and invariants: `lib/core/reference/code-architecture/app-layer-theory.md`. This file covers Dart patterns for the application module.

The application module is the entry point. It owns: `main.dart`, `engine.dart`, DI orchestration, centralized routing, global providers, and entry-point screens.

---

## main.dart <!-- 10 -->

`main.dart` is a thin delegate that reads the env type and forwards to `engine.start()`. It also declares the background entrypoint for headless call rejection.

```dart
// lib/main.dart
import 'package:qontak_chat_app/engine.dart' as engine;

void main() => engine.start(envType: engine.getEnvType());

@pragma('vm:entry-point')
void backgroundRejectEntry() => engine.backgroundRejectCallHandler();
```

---

## Engine (Startup Orchestrator) <!-- 42 -->

`engine.dart` owns the full initialization sequence inside `runZonedGuarded`. Add new initialization steps here in dependency order.

```dart
// lib/engine.dart
void start({EnvType envType = EnvType.staging}) =>
    runZonedGuarded<Future<void>>(
      () async {
        final env = Env(envType: envType);
        WidgetsFlutterBinding.ensureInitialized();

        // 1. Firebase
        if (Firebase.apps.isEmpty) await Firebase.initializeApp();
        if (Platform.isIOS) FirebaseMessaging.onBackgroundMessage(fcmBackgroundHandler);

        // 2. Database schemas
        await DatabaseService.instance.init([
          ActivePackageDBSchema,
          MKRFlagFeatureDBSchema,
          ...ContactDependency.getDatabaseSchemas(),
        ]);

        // 3. DI — all feature modules
        await ChatDi.initDependency(
          baseUrl: env.data.apiBaseUrl,
          // ... other required params
        );

        // 4. Feature flags
        await FeatureFlagHelper.instance.initialize(...);

        // 5. App-level services
        coreDependency<MoEngageFlutter>().initialise();
        coreDependency<FlavorConfiguration>().initialize(flavor);

        // 6. Bricks (auth SDK)
        await Bricks.init(BrickFlutterConfiguration(..., modules: [AuthModule()]));

        // 7. MKRLog
        await qontakCommonDependency<MkrLogHelper>().init(...);

        // 8. Error handlers
        FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;
        PlatformDispatcher.instance.onError = (error, stack) {
          FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
          return true;
        };

        runApp(AppProvider(child: App(environment: envType.name)));
      },
      (error, stack) => FirebaseCrashlytics.instance.recordError(error, stack),
    );
```

---

## App Widget <!-- 20 -->

`App` is a `StatefulWidget` with `WidgetsBindingObserver` that configures `MaterialApp` (not `MaterialApp.router`). Navigation uses `Navigator` + `onGenerateRoute`.

```dart
// lib/app.dart
class App extends StatefulWidget {
  const App({required this.environment, super.key});
  final String environment;
  // ...
}

class _AppState extends State<App> with WidgetsBindingObserver {
  final routeManager = AppRouteManger();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      initialRoute: QontakAppRoute.splash,
      onGenerateRoute: routeManager.onGenerateRoute,
      navigatorKey: NavigationHelperImpl.navigatorKey,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        QontakChatLocalizations.delegate,
        ChatConversationLocalizations.delegate,
        // ... all feature package delegates listed explicitly
      ],
      supportedLocales: [Localization.enLocale],
      navigatorObservers: [
        coreDependency<RouteObserver<PageRoute>>(),
        coreDependency<MKRLogRouteObserver>(),
      ],
    );
  }
}
```

---

## DI Orchestration <!-- 30 -->

No `@InjectableInit` or code generation in the app layer. DI uses static methods with manual `GetIt.registerLazySingleton` / `registerFactory`.

```dart
// lib/config/di/chat_di.dart
class ChatDi {
  static Future<void> initDependency({
    required String baseUrl,
    // ... all required env params
  }) async {
    // 1. Core (networking, logger, base services)
    await CoreDependency.registerCore(baseUrl: baseUrl, ...);

    // 2. Feature packages — each owns its own registration
    ContactDependency.registerContact(...);
    ComposerDependency.registerComposer(...);
    await MessagingDependency.registerMessaging(...);
    await InboxDependency.registerInbox(...);
    ConversationDependency.registerConversation(...);
    CallDependency.registerCall(...);

    // 3. App-level (depends on feature packages being registered first)
    MainDependency.registerMain();
    ChatNotificationDependency.registerChatNotification(...);
  }
}
```

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

**Rules:**
- `CoreDependency.registerCore()` always runs before feature packages
- Feature packages run before `MainDependency.registerMain()`
- BLoCs use `registerFactory` (new instance each time); services and repositories use `registerLazySingleton`
- Never use `@injectable`, `@lazySingleton`, or `@InjectableInit` annotations in the app module

---

## Global BLoC Provider <!-- 20 -->

App-wide BLoCs (available across all routes) are wired in `AppProvider` using `MultiBlocProvider`. Route-scoped BLoCs are wired in `route_manager.dart`.

```dart
// lib/provider.dart
class AppProvider extends StatelessWidget {
  const AppProvider({required this.child, super.key});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => ChatFeatureFlagCubit(featureFlagHelper: qontakCommonDependency(), ...)),
        BlocProvider(create: (_) => UserProfileBloc(getUserInfo: coreDependency(), ...)),
        BlocProvider(create: (_) => BottomNavigationBloc(getUnreadRoomCount: mainDependency(), ...)),
        BlocProvider<AppInitializationBloc>(
          create: (context) => AppInitializationBloc(
            useCasePackageBloc: context.read<UseCasePackageBloc>(),
            userProfileBloc: context.read<UserProfileBloc>(),
            organizationBloc: context.read<GetCurrentOrganizationBloc>(),
            crsPermissionsBloc: context.read<GetCrsPermissionsBloc>(),
            chatFeatureFlagCubit: context.read<ChatFeatureFlagCubit>(),
          ),
        ),
        // ... all global BLoCs
      ],
      child: child,
    );
  }
}
```

Note: `AppInitializationBloc` is an orchestrator that subscribes to sibling BLoCs via `context.read` and drives a multi-step initialization flow (package check → profile → permissions).

---

## AppInitializationBloc (Orchestrator BLoC) <!-- 32 -->

`AppInitializationBloc` is a special orchestrator BLoC that drives a multi-step sequential initialization flow by subscribing to sibling BLoCs via `StreamSubscription`. It does not own any use cases directly — it reacts to state changes from other BLoCs already in the `AppProvider` tree.

```dart
// lib/presentation/bloc/app_initialization/app_initialization_bloc.dart
class AppInitializationBloc extends Bloc<AppInitializationEvent, AppInitializationState> {
  AppInitializationBloc({
    required UseCasePackageBloc useCasePackageBloc,
    required UserProfileBloc userProfileBloc,
    required GetCurrentOrganizationBloc organizationBloc,
    required GetCrsPermissionsBloc crsPermissionsBloc,
    required ChatFeatureFlagCubit chatFeatureFlagCubit,
  }) : super(const AppInitializationState()) {
    on<_PackageChecked>(_onPackageChecked);
    on<_ProfileLoaded>(_onProfileLoaded);
    on<_PermissionsLoaded>(_onPermissionsLoaded);

    // Subscribe to sibling BLoCs — drives sequential initialization
    _packageSub = useCasePackageBloc.stream.listen((state) {
      if (state.packageState.status.isHasData) add(const _PackageChecked());
    });
    _profileSub = userProfileBloc.stream.listen((state) {
      if (state.profileState.status.isHasData) add(const _ProfileLoaded());
    });
    _permissionsSub = crsPermissionsBloc.stream.listen((state) {
      if (state.permissionsState.status.isHasData) add(const _PermissionsLoaded());
    });
  }

  late final StreamSubscription _packageSub;
  late final StreamSubscription _profileSub;
  late final StreamSubscription _permissionsSub;

  @override
  Future<void> close() {
    _packageSub.cancel();
    _profileSub.cancel();
    _permissionsSub.cancel();
    return super.close();
  }
}
```

**Invariants:**
- Constructed inside `AppProvider` using `context.read<SiblingBloc>()` — sibling BLoCs must appear earlier in the `MultiBlocProvider` list
- Internal events (`_PackageChecked`, `_ProfileLoaded`, etc.) use a `_` prefix — they are not dispatched from the UI
- Each `StreamSubscription` is cancelled in `close()` — prevents leaks
- Never used for feature-level orchestration — this pattern is app-startup only; feature BLoCs handle their own sequencing

**When to use:** Only for startup flows where Step N cannot begin until Step N-1 is confirmed complete and each step is driven by a separate BLoC already registered globally.

---

## Firebase Background Message Handling <!-- 18 -->

Firebase background messages require a top-level Dart function annotated with `@pragma('vm:entry-point')`. This tells the Dart VM to preserve the function in AOT-compiled builds (it would otherwise be tree-shaken away).

```dart
// lib/main.dart — top-level, outside any class
@pragma('vm:entry-point')
void backgroundRejectEntry() => engine.backgroundRejectCallHandler();

// lib/engine.dart — registered during startup
if (Platform.isIOS) {
  FirebaseMessaging.onBackgroundMessage(fcmBackgroundHandler);
}

// Top-level handler (must be top-level, not a method)
@pragma('vm:entry-point')
Future<void> fcmBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // handle message — runs in a separate Dart isolate
}
```

**Invariants:**
- Handler must be a **top-level function** — not a static method, not a lambda. Flutter spawns a separate isolate for it.
- `@pragma('vm:entry-point')` is required on every function that serves as an isolate entry point — omitting it causes AOT tree-shaking to remove it silently.
- `Firebase.initializeApp()` must be called inside the background handler — the isolate has no shared state with the main isolate.
- iOS-only registration: `FirebaseMessaging.onBackgroundMessage` is guarded by `Platform.isIOS` in `engine.dart`.

---

## Analytics & Error Reporting <!-- 12 -->

Wired directly in `engine.dart` — no separate analytics setup file:

```dart
// In engine.dart start()
FlutterError.onError = (errorDetails) {
  FirebaseCrashlytics.instance.recordFlutterFatalError(errorDetails);
};
PlatformDispatcher.instance.onError = (error, stack) {
  FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
  return true;
};
FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;
```

---

## Planner Search Patterns <!-- 8 -->

| Scope key | Path | Grep hint |
|---|---|---|
| `di` | `lib/config/di/chat_di.dart`, `lib/config/di/main_dependency.dart` | `ChatDi`, `MainDependency`, `registerMain` |
| `route` | `lib/route_manager.dart` | `AppRouteManger`, `QontakAppRoute`, `onGenerateRoute` |
| `provider` | `lib/provider.dart` | `AppProvider`, `MultiBlocProvider` |
| `engine` | `lib/engine.dart` | `start(`, `initDependency`, `runApp` |
