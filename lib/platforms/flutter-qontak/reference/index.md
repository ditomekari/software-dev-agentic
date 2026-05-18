# Flutter Qontak — Reference Index

Theory lives in `lib/core/reference/code-architecture/`. This platform covers Flutter/Dart implementation patterns for modular (melos workspace) architecture.

| File | Sections | Use when |
|---|---|---|
| `reference/project.md` | Workspace layout, module types, dependency graph, package naming, DTO naming | Understanding overall structure or planning a new module |
| `reference/code-architecture/domain-impl.md` | Entities, Repository Interfaces, Use Cases, Domain Services, Failure, Enums | Creating domain layer artifacts in any feature package |
| `reference/code-architecture/data-impl.md` | Response/Request/Db models, Mappers, Data Sources, Repository Impl, AppException | Creating data layer artifacts |
| `reference/code-architecture/presentation-impl.md` | ViewDataState, Events, States, BLoC, Screen Structure, BlocListener, Cubit | Creating BLoC/Cubit, screens, or widgets |
| `reference/code-architecture/error-handling-impl.md` | Error flow, AppException, ErrorInterceptor, Validation errors, Error UI | Mapping exceptions to Failures, error display patterns |
| `reference/code-architecture/app-layer-impl.md` | main.dart, Runner, DI aggregation, ModuleRegistrar, Route registration | Wiring a new module into the app, app-level setup |
| `reference/code-architecture/navigation-impl.md` | Route constants, BaseModule routes, Cross-module Navigation API, Auth guard, Deep links | Navigation setup per module or cross-module navigation |
| `reference/code-architecture/modular-structure-impl.md` | BaseModule contract, Feature/Shared module setup, ModuleRegistrar, Dependencies module | Creating a new feature package or shared module |
| `reference/code-architecture/module-communication-impl.md` | Module API pattern, Navigation API pattern | Sharing data/behavior between feature modules |
| `reference/code-architecture/di-impl.md` | Per-module @InjectableInit, aggregation, Module API registration, scoping rules | Wiring DI in a new module |
| `reference/code-architecture/testing-impl.md` | Per-package test structure, melos test, BLoC/UseCase/Mapper/Module API tests | Writing tests in any feature package |
| `reference/code-architecture/syntax-conventions-impl.md` | Null safety extensions, Unlocalized text, Code style, Import order, Naming | Cross-cutting coding standards |
| `reference/code-architecture/utilities-impl.md` | Logger, HTTP client, StorageService, DateService, AuthInterceptor | Shared infrastructure in `[prefix]_core` |
| `reference/code-architecture/localization-impl.md` | Per-feature .arb files, l10n.yaml, LocalizationsDelegate via BaseModule | Adding translations to a feature package |
| `reference/code-architecture/flavor-impl.md` | Flavor config, bundle IDs per flavor, Envied, Firebase per flavor | Flavor setup or adding a new environment |
| `reference/code-architecture/tech-stack-impl.md` | Recommended dependencies with rationale, pubspec.yaml patterns, linter | Choosing a library, setting up a new package |

**Grep pattern:** `Grep "^## <Section>" reference/code-architecture/<topic>-impl.md` — returns heading + `<!-- N -->` line count for bounded Read.
