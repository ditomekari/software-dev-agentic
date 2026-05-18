# Flutter Qontak — Reference Index

Theory lives in `lib/core/reference/code-architecture/`. This platform covers Flutter/Dart implementation patterns for the `mobile-qontak-chat` architecture: centralized routing, manual GetIt DI, and external feature packages.

| File | Sections | Use when |
|---|---|---|
| `reference/project.md` | App layout, module types, dependency graph, package naming, DTO naming | Understanding overall structure or planning a new feature |
| `reference/code-architecture/domain-impl.md` | Entities, Repository Interfaces, Use Cases, Domain Services, Failure, Enums | Creating domain layer artifacts |
| `reference/code-architecture/data-impl.md` | Response/Request/Db models, Mappers, Data Sources, Repository Impl, AppException | Creating data layer artifacts |
| `reference/code-architecture/presentation-impl.md` | ViewDataState (status API), Events, States, BLoC (named params), Screen Structure, BlocListener | Creating BLoC, screens, or widgets |
| `reference/code-architecture/error-handling-impl.md` | Error flow, AppException, ErrorInterceptor, Validation errors, Error UI | Mapping exceptions to Failures, error display patterns |
| `reference/code-architecture/app-layer-impl.md` | main.dart, engine.dart, ChatDi, MainDependency, AppProvider, route_manager | Wiring a new BLoC or screen into the app |
| `reference/code-architecture/navigation-impl.md` | QontakAppRoute, AppRouteManger, NavigationHelper.pushNamed, Arguments pattern | Adding a new route or navigating between screens |
| `reference/code-architecture/modular-structure-impl.md` | BaseModule contract (aspirational), feature module setup, ModuleRegistrar | Planning a new feature module structure |
| `reference/code-architecture/module-communication-impl.md` | Module API pattern, typedef callback injection via ChatDi | Sharing data/behavior between feature packages |
| `reference/code-architecture/di-impl.md` | Manual GetIt registration, registerFactory/registerLazySingleton, ChatDi order | Wiring DI for a new BLoC, use case, or repository |
| `reference/code-architecture/testing-impl.md` | Per-package test structure, BLoC/UseCase/Mapper tests | Writing tests in any feature package |
| `reference/code-architecture/syntax-conventions-impl.md` | Null safety extensions, Unlocalized text, Code style, Import order, Naming | Cross-cutting coding standards |
| `reference/code-architecture/utilities-impl.md` | Logger, HTTP client, StorageService, DateService, AuthInterceptor | Shared infrastructure in `chat_core` |
| `reference/code-architecture/localization-impl.md` | Per-feature .arb files, l10n.yaml, LocalizationsDelegate in MaterialApp | Adding translations to a feature package |
| `reference/code-architecture/flavor-impl.md` | DartDefine + EnvType + EnvData (no envied), Firebase per flavor | Flavor setup or adding a new environment |
| `reference/code-architecture/tech-stack-impl.md` | Recommended dependencies with rationale, pubspec.yaml patterns, linter | Choosing a library, setting up a new package |

**Grep pattern:** `Grep "^## <Section>" reference/code-architecture/<topic>-impl.md` — returns heading + `<!-- N -->` line count for bounded Read.
