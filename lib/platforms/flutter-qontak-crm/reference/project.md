# Flutter Qontak CRM — Project Structure & Conventions

---

## App Overview <!-- 10 -->

**Package name:** `qontak_crm`
**Description:** Qontak CRM mobile application — a full-featured CRM for managing contacts, companies, deals, tasks, notes, products, and live GPS tracking.

The repository is a **Melos monorepo**. The root application package (`qontak_crm`) is the app shell only. All feature code lives as independent Flutter packages under `features/`.

The app supports **multiple flavors** (main Qontak CRM, Pyridam, KRAS SalesGo) through `FlavorChecker` and environment-specific `.env.*` files.

---

## Repo Layout <!-- 30 -->

```
/ (monorepo root)
├── lib/                                    ← application module (app shell only)
│   ├── main.dart                           ← entry point
│   ├── engine.dart                         ← initialization (Firebase → ObjectBox → DI → runApp)
│   ├── app.dart                            ← MaterialApp widget
│   ├── configs/
│   │   ├── di/
│   │   │   ├── crm_di.dart                 ← CrmDi (orchestrates all module DI)
│   │   │   └── qontak_crm_dependency.dart  ← app-level GetIt registrations
│   │   ├── constants/                      ← endpoints, dart defines, colors, semantics
│   │   ├── environment/                    ← Env, EnvData per flavor
│   │   ├── l10n/                           ← localization delegates wiring
│   │   ├── modules.dart                    ← featureModules list (List<BaseModule>)
│   │   └── objectbox_initializer.dart
│   ├── data/                               ← app-level data layer (auth token only)
│   ├── domain/                             ← app-level domain layer (auth token only)
│   ├── presentation/                       ← app-level BLoCs + screens (login, bottom nav)
│   └── gen/                                ← generated assets (flutter_gen) and l10n
├── features/
│   ├── crm_company/                        ← Company feature package
│   ├── crm_contact/                        ← Contact feature package
│   ├── crm_core/                           ← Core shared package (base classes, BLoC bases)
│   ├── crm_deal/                           ← Deal feature package
│   ├── crm_live_gps/                       ← Live GPS feature package
│   ├── crm_misc/                           ← Miscellaneous shared utilities
│   ├── crm_note/                           ← Note feature package
│   ├── crm_product/                        ← Product feature package
│   ├── crm_task/                           ← Task feature package
│   ├── crm_ticket/                         ← Ticket feature package
│   ├── qontak_custom_form/                 ← Custom form package
│   ├── qontak_common/                      ← Cross-app utilities (UseCase, ViewDataState, Failure)
│   ├── qontak_component_lib/               ← Shared UI component library
│   └── shared/
│       ├── crm_dependency/                 ← GetIt re-exports (crm_dependency.dart)
│       └── qontak_dependency/              ← GetIt re-exports (qontak_dependency.dart)
└── pubspec.yaml                            ← root app pubspec; features are path dependencies
```

---

## Module Types <!-- 12 -->

| Type | What it contains | Role |
|---|---|---|
| **Application module** (`lib/`) | `main.dart`, engine, DI orchestration, routing, entry screens | The Flutter app shell |
| **Feature packages** (`features/crm_*`) | Complete feature (data + domain + presentation) | Local path dependency |
| **Core package** (`crm_core`) | Base classes, `GetIndexBaseBloc`, networking base | Shared via dependency |
| **Common package** (`qontak_common`) | `UseCase`, `ViewDataState`, `Failure`, `QontakMonitor`, `DatabaseService` | Shared via dependency |
| **Component library** (`qontak_component_lib`) | Shared UI components | Shared via dependency |

---

## Dependency Graph <!-- 8 -->

```
qontak_crm (application)
  ├── crm_core
  ├── qontak_common (re-exported via crm_core)
  ├── crm_company
  ├── crm_contact
  ├── crm_deal
  ├── crm_task
  ├── crm_note
  ├── crm_ticket
  ├── crm_product
  ├── crm_live_gps
  └── qontak_component_lib
```

Feature packages depend on `crm_core` and `qontak_common` — never on each other directly.
Cross-feature data sharing uses dependency accessor cross-resolution at the DI layer.

---

## Package Naming Conventions <!-- 10 -->

| What | Pattern | Example |
|---|---|---|
| CRM feature package | `crm_<domain>` | `crm_company`, `crm_deal` |
| Qontak shared package | `qontak_<domain>` | `qontak_common`, `qontak_component_lib` |
| DI class | `Qontak<Feature>Dependency` | `QontakCompanyDependency` |
| DI accessor | `qontak<Feature>Dependency` | `qontakCompanyDependency` |
| Module class | `CRM<Feature>Module` / `Qontak<Feature>Module` | `CRMCompanyModule` |

---

## Model Naming (Data Layer) <!-- 10 -->

| Type | Suffix | Example |
|---|---|---|
| API response model (feature) | `Response` | `CompanyResponse` |
| API request body (feature) | `Request` | `CompanyFilterRequest` |
| API model (app root) | `Model` | `AuthTokenModel` |
| Isar DB entity | `Db` | `CompanyDb` |
| ObjectBox entity | `ObjectBox` | `CompanyObjectBox` |
| Domain entity | _(none)_ | `Company` |

---

## App Rules <!-- 8 -->

- `engine.dart` owns initialization order: Firebase → ObjectBox → DI → `runApp`
- The application module (`lib/`) contains only app-shell concerns: auth, bottom navigation, DI orchestration, routing
- Feature code lives exclusively in `features/<package_name>/lib/src/`
- Feature packages export their public API through `lib/<package_name>.dart`
- BLoCs are NOT registered in `get_it` — instantiated inline in `route_manager.dart` via `BlocProvider`
- No `injectable` annotations — all DI is manual via `registerLazySingleton` / `registerFactory`
