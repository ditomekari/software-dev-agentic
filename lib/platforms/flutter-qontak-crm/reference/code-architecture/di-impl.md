# Flutter Qontak CRM — Dependency Injection

> Concepts and invariants: `lib/core/reference/code-architecture/di-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

`get_it` is used manually — no `injectable` code generation (`@InjectableInit`, `@lazySingleton`, `@singleton`, `@factoryMethod` annotations are forbidden).

---

## DI Architecture <!-- 18 -->

The app module (`lib/configs/di/crm_di.dart`) is the DI root. Feature packages each expose a static `register*()` method. `CrmDi.initDependency()` orchestrates the registration order.

```
engine.dart
  └── CrmDi.initDependency()
        ├── QontakCommonDependency.registerCommon() ← register first, await allReady()
        ├── QontakCoreDependency.registerCore()
        ├── QontakCompanyDependency.registerCompany()
        ├── QontakContactDependency.registerContact()
        ├── QontakDealDependency.registerDeal()
        ├── QontakTaskDependency.registerTask()
        ├── QontakNoteDependency.registerNote()
        ├── QontakTicketDependency.registerTicket()
        ├── QontakProductDependency.registerProduct()
        └── QontakCrmDependency.registerApp()    ← app-level; depends on all above
```

**App-level orchestration order:**
1. Register `QontakCommonDependency` first and `await allReady()`.
2. Register `QontakCoreDependency`.
3. Register all feature dependencies in any order.
4. Register app-level `QontakCrmDependency` last.

---

## Feature Accessor Pattern <!-- 12 -->

Each feature (and the app shell) has a module-scoped accessor. All features share the **same** `GetIt.instance` — the named variables are aliases, not separate containers.

```dart
// features/crm_company/lib/src/config/di/qontak_company_dependency.dart
final qontakCompanyDependency = GetIt.instance;

// Cross-module resolution — use the source feature's accessor:
final qontakCommonDependency = GetIt.instance;   // from qontak_common
final qontakCoreDependency = GetIt.instance;     // from crm_core
```

---

## Feature DI Class Pattern <!-- 25 -->

```dart
class QontakCompanyDependency {
  static void registerCompany() {
    _registerDatabase();
    _registerObjectBox();
    _registerCompanyData();
    _registerCompanyDomain();
  }

  static void _registerDatabase() {
    qontakCompanyDependency.registerLazySingleton<CompanyIsarDatabase>(
      () => CompanyIsarDatabase(DatabaseService.instance),
    );
  }

  static void _registerObjectBox() {
    qontakCompanyDependency.registerLazySingleton<ObjectBoxStore>(
      () => ObjectBoxStore(qontakCommonDependency()),
    );
  }

  static void _registerCompanyData() {
    qontakCompanyDependency
      ..registerLazySingleton<CompanyDataLocalDataSource>(
          () => CompanyDataLocalDataSourceImpl(
                database: qontakCompanyDependency(),
                objectBoxStore: qontakCompanyDependency(),
              ))
      ..registerLazySingleton<CompanyRemoteDataSource>(
          () => CompanyRemoteDataSourceImpl(
                baseApi: qontakCommonDependency(),
              ))
      ..registerLazySingleton<CompanyRepository>(
          () => CompanyRepositoryImpl(
                remoteDataSource: qontakCompanyDependency(),
                localDataSource: qontakCompanyDependency(),
              ));
  }

  static void _registerCompanyDomain() {
    qontakCompanyDependency
      ..registerLazySingleton(
          () => GetCompanyListUseCase(repository: qontakCompanyDependency()))
      ..registerLazySingleton(
          () => GetCompanyByIdUseCase(repository: qontakCompanyDependency()))
      ..registerLazySingleton(
          () => AddCompanyUseCase(repository: qontakCompanyDependency()))
      ..registerLazySingleton(
          () => DeleteCompanyUseCase(repository: qontakCompanyDependency()));
  }
}
```

---

## Scope Rules <!-- 13 -->

| GetIt method | Scope | Use for |
|---|---|---|
| `registerLazySingleton` | Singleton, created on first access | DataSources, Repositories, Use Cases, DB services |
| `registerSingleton` | Singleton, created eagerly | Services requiring immediate init |
| `registerFactory` | New instance per call | BLoCs, Cubits — stateful, one per screen |
| `registerLazySingleton<IFace>(() => Impl())` | Singleton under abstract type | Repository and DataSource implementations |

**Never use `registerLazySingleton` for BLoCs** — BLoC holds mutable state. BLoCs are instantiated inline in `route_manager.dart` inside `BlocProvider`, not registered in `get_it` at all.

---

## BLoC Instantiation (Route-Scoped) <!-- 14 -->

BLoCs are instantiated in `route_manager.dart` pulling use cases from the dependency accessor:

```dart
// lib/presentation/route_manager.dart
case AppRoute.company:
  return MaterialPageRoute(
    settings: settings,
    builder: (_) => BlocProvider(
      create: (_) => CompanyBloc(
        getCompanyListUseCase: qontakCompanyDependency(),
        filterCompanyUseCase: qontakCompanyDependency(),
      ),
      child: const CompanyScreen(),
    ),
  );

// Multi-BLoC route
case AppRoute.companyDetail:
  return MaterialPageRoute(
    settings: settings,
    builder: (_) => MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (_) => CompanyDetailBloc(
            getCompanyByIdUseCase: qontakCompanyDependency(),
          ),
        ),
        BlocProvider(
          create: (_) => NoteListBloc(
            getNoteListUseCase: qontakNoteDependency(),
          ),
        ),
      ],
      child: CompanyDetailScreen(arguments: settings.arguments as CompanyDetailArgument),
    ),
  );
```

---

## Cross-Feature Resolution <!-- 10 -->

Use the source feature's accessor to pull cross-module dependencies:

```dart
// In QontakContactDependency — resolving company data source from crm_company:
qontakContactDependency.registerLazySingleton<ContactRepository>(
  () => ContactRepositoryImpl(
    remoteDataSource: qontakContactDependency(),
    companyLocalDataSource: qontakCompanyDependency(), // ← cross-module
    baseApi: qontakCommonDependency(),                 // ← from qontak_common
  ),
);
```

---

## Testing with DI <!-- 8 -->

Prefer constructor injection — pass mock instances directly, no `GetIt` manipulation:

```dart
setUp(() {
  mockGetCompanyListUseCase = MockGetCompanyListUseCase();
  bloc = CompanyBloc(
    getCompanyListUseCase: mockGetCompanyListUseCase,
  );
});

tearDown(() => bloc.close());
```

When a test must interact with `GetIt.instance`, reset it in `tearDown`:
```dart
tearDown(() => GetIt.instance.reset());
```
