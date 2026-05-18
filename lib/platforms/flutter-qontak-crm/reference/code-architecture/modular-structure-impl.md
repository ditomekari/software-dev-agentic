# Flutter Qontak CRM — Modular Structure

> Concepts and invariants: `lib/core/reference/code-architecture/domain-theory.md`. This file covers Dart code patterns for creating and wiring feature modules in the CRM monorepo.

The CRM uses a Melos monorepo. The root application package (`qontak_crm`) contains the app shell. All feature code lives in `features/` as independent Flutter packages.

---

## BaseModule Contract <!-- 15 -->

`BaseModule` lives in `crm_core` and defines what the application module needs from every feature module:

```dart
// features/crm_core/lib/src/base/base_module.dart
abstract class BaseModule {
  LocalizationsDelegate<dynamic>? localizationsDelegate();
  List<CollectionSchema> collectionSchemas();
}
```

Every feature package exports a `<PREFIX>Module` class implementing `BaseModule`:
- `localizationsDelegate()` — returns the feature's active-flavor `LocalizationsDelegate`, or `null` if no translations
- `collectionSchemas()` — returns Isar `CollectionSchema` list, or `[]` if no Isar models

---

## Feature Module Implementation <!-- 20 -->

```dart
// features/crm_company/lib/src/crm_company.dart
import 'package:crm_core/crm_core.dart';
import 'gen/l10n/company_localizations.dart';
import 'data/database/company_db.dart'; // Isar schema

class CRMCompanyModule implements BaseModule {
  @override
  LocalizationsDelegate<dynamic>? localizationsDelegate() {
    if (FlavorChecker.isPyridam) return PyridamCompanyLocalizations.delegate;
    if (FlavorChecker.isKrasSalesGo) return KrasCompanyLocalizations.delegate;
    return CompanyLocalizations.delegate;
  }

  @override
  List<CollectionSchema> collectionSchemas() => [CompanyDbSchema];
}
```

---

## featureModules Registration <!-- 10 -->

```dart
// lib/configs/modules.dart
final List<BaseModule> featureModules = [
  CRMCompanyModule(),
  CRMContactModule(),
  CRMDealModule(),
  CRMTaskModule(),
  CRMNoteModule(),
  CRMTicketModule(),
  CRMProductModule(),
  CRMLiveGpsModule(),
  QontakCommonModule(),
];
```

All modules are consumed by `app.dart` to aggregate localization delegates and by `engine.dart` to register Isar schemas.

---

## Feature Package Internal Layout <!-- 20 -->

Every feature package follows this structure under `lib/src/`:

```
features/crm_company/
├── lib/
│   ├── crm_company.dart              ← public barrel export
│   ├── gen/                          ← generated files (objectbox, l10n)
│   └── src/
│       ├── crm_company.dart          ← BaseModule implementation
│       ├── config/
│       │   ├── constants/            ← endpoint constants, semantic labels, logging constants
│       │   ├── di/                   ← QontakCompanyDependency
│       │   ├── l10n/                 ← l10n barrel
│       │   ├── objectbox/            ← ObjectBox store + adapters
│       │   └── utils/                ← feature-specific utility classes
│       ├── data/
│       │   ├── data_sources/
│       │   │   ├── local/            ← abstract + impl local data source
│       │   │   └── remote/           ← abstract + impl remote data source
│       │   ├── database/             ← Isar + ObjectBox DB implementations
│       │   ├── mappers/              ← static mapper classes
│       │   ├── models/
│       │   │   ├── local/            ← Isar Db models, ObjectBox models
│       │   │   └── remote/           ← API Response/Request models
│       │   └── repositories/         ← repository implementations
│       ├── domain/
│       │   ├── entities/             ← domain entities (@freezed, no suffix)
│       │   ├── repositories/         ← abstract repository interfaces
│       │   └── usecases/             ← use case classes
│       └── presentation/
│           ├── bloc/                 ← BLoC folders, one per BLoC
│           ├── mixins/               ← screen mixins
│           ├── screens/              ← screen widgets
│           └── widgets/              ← feature-local reusable widgets
├── pubspec.yaml
└── analysis_options.yaml
```

---

## Shared Packages <!-- 12 -->

| Package | Purpose | Access via |
|---|---|---|
| `crm_core` | Base classes, networking base, BLoC bases, `GetIndexBaseBloc` | `qontakCoreDependency` |
| `qontak_common` | `UseCase`, `ViewDataState`, `Failure`, `QontakMonitor`, `DatabaseService` | `qontakCommonDependency` |
| `qontak_component_lib` | Shared UI components | direct import |
| `crm_misc` | Cross-feature utility classes | direct import |
| `shared/crm_dependency` | GetIt re-exports for crm packages | `crm_dependency.dart` |
| `shared/qontak_dependency` | GetIt re-exports for qontak packages | `qontak_dependency.dart` |

---

## Adding a New Feature Package <!-- 12 -->

1. Create `features/crm_<domain>/` with the standard layout above
2. Declare it in `melos.yaml` under `packages:`
3. Add it to root `pubspec.yaml` as a path dependency
4. Implement `BaseModule` and add to `featureModules` in `lib/configs/modules.dart`
5. Create `Qontak<Feature>Dependency` and call `register<Feature>()` from `CrmDi.initDependency()`
6. Run `melos bootstrap` to re-link packages

---

## Public API Contract <!-- 8 -->

Each feature package exports only its public API through the barrel file:

```dart
// features/crm_company/lib/crm_company.dart
export 'src/crm_company.dart';                              // BaseModule
export 'src/domain/entities/company.dart';
export 'src/domain/repositories/company_repository.dart';
export 'src/config/di/qontak_company_dependency.dart';     // DI accessor
// Do NOT export data layer types (models, datasources, mapper, repositoryImpl)
```

Cross-feature code must import via the public barrel — never via relative paths across package boundaries.
