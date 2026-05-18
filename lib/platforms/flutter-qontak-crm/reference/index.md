# Flutter Qontak CRM — Reference Index

Theory lives in `lib/core/reference/code-architecture/`. This platform covers Flutter/Dart implementation patterns for the `qontak_crm` monorepo architecture: Melos feature packages, manual GetIt DI, dual-DB migration (Isar → ObjectBox), and multi-flavor support.

| File | Sections | Use when |
|---|---|---|
| `reference/project.md` | App layout, module types, dependency graph, package naming, model naming | Understanding overall structure or planning a new feature package |
| `reference/code-architecture/modular-structure-impl.md` | BaseModule contract, feature package layout, featureModules registration, public API | Adding a new feature package or understanding the monorepo structure |
| `reference/code-architecture/domain-impl.md` | Entities, Repository Interfaces, Use Cases (naming: `<Verb><Entity>UseCase`), Domain Services | Creating domain layer artifacts |
| `reference/code-architecture/data-impl.md` | Response/Request/Db/ObjectBox models, Mappers, DataSources (BaseApi), RepositoryImpl, dual-DB, DI registration | Creating data layer artifacts |
| `reference/code-architecture/presentation-impl.md` | ViewDataState (status API), Events, States, BLoC (named params, sequential()), Screen Structure, BlocListener | Creating BLoC, screens, or widgets |
| `reference/code-architecture/di-impl.md` | CrmDi orchestration order, feature DI class pattern, GetIt scope rules, BLoC instantiation, cross-feature resolution | Wiring DI for a new use case, repository, or BLoC |
| `reference/code-architecture/error-handling-impl.md` | Error flow, try/catch vs TaskEither, QontakMonitor logging, BLoC error pattern, error display | Mapping exceptions to Failures, error display patterns |
| `reference/code-architecture/navigation-impl.md` | AppRoute constants, route_manager.dart, screen arguments, BLoC→navigation side effects | Adding a new route or navigating between screens |
| `reference/code-architecture/app-layer-impl.md` | engine.dart, CrmDi, app.dart, featureModules, BaseModule, app-shell concerns | Wiring a new feature module into the app shell |
| `reference/code-architecture/testing-impl.md` | Per-package test structure, mock generation, BLoC/UseCase/Mapper tests, test naming | Writing tests in any feature package |
| `reference/code-architecture/syntax-conventions-impl.md` | Naming table, file placement rules, import order, null safety, code style, linter | Cross-cutting coding standards and naming |
| `reference/code-architecture/utilities-impl.md` | QontakMonitor, BaseApi/mekari_network, DatabaseService/Isar, ObjectBoxStore, FlavorChecker, DataSourceSwapHelper, assets | Shared infrastructure and platform utilities |
| `reference/code-architecture/ui-impl.md` | qontak_component_lib, widget placement, screen structure, assets, flavor-gated UI | UI component usage and screen layout patterns |
| `reference/code-architecture/tech-stack-impl.md` | Full dependency table, pubspec.yaml patterns, melos.yaml, linter | Choosing a library, adding a new package, build tooling |

**Grep pattern:** `Grep "^## <Section>" reference/code-architecture/<topic>-impl.md` — returns heading + `<!-- N -->` line count for bounded Read.
