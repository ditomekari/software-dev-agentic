# Flutter Qontak CRM — Tech Stack

Standard dependencies for the Qontak CRM monorepo.

---

## Core Dependencies <!-- 25 -->

| Concern | Library | Notes |
|---|---|---|
| State management | `flutter_bloc` | Sole state pattern — via `crm_core`/`crm_dependency.dart` |
| DI / service locator | `get_it` (manual) | No `injectable`/code-gen — manual `registerFactory`/`registerLazySingleton` |
| Networking | `mekari_network` (internal) | Wraps HTTP; provides `BaseApi` with auth token refresh |
| Serialization | `freezed` + `json_serializable` | `copyWith`, sealed classes, DTO models with `fromJson` |
| Local database (primary) | `isar` | Via `DatabaseService.instance` — legacy, migration target is ObjectBox |
| Local database (migration) | `objectbox` | Via `ObjectBoxStore` per feature — new features use this only |
| Asset generation | `flutter_gen` | Class: `QontakCRMAssets` — access assets via generated class, not raw paths |
| Localization | `flutter_localizations` + ARB files | Per-feature and per-flavor ARB files |
| Code generation runner | `build_runner` | Run after adding `@freezed`, `@JsonSerializable`, `@GenerateNiceMocks`, ObjectBox entities |
| Env config | `envied` | `.env.production` / `.env.staging` per flavor |
| Crash monitoring | `QontakMonitor` | Wraps Firebase Crashlytics — call `.logCrashMonitor(logName:)` |
| Monorepo tooling | `melos` | Feature packages as local path dependencies; `melos run test` for all packages |
| Unit test mocking | `mockito` | Code-gen mocks via `@GenerateNiceMocks` |
| BLoC testing | `bloc_test` | `blocTest()` for BLoC/Cubit unit tests |

---

## pubspec.yaml Patterns <!-- 20 -->

The root app (`qontak_crm`) declares feature packages as local path dependencies via melos:

```yaml
# pubspec.yaml (root application)
name: qontak_crm

dependencies:
  flutter:
    sdk: flutter

  # Feature packages (local path via melos — not pub)
  crm_company:
    path: features/crm_company
  crm_contact:
    path: features/crm_contact
  crm_core:
    path: features/crm_core
  crm_deal:
    path: features/crm_deal
  qontak_common:
    path: features/qontak_common
  qontak_component_lib:
    path: features/qontak_component_lib

  # External / internal packages (pinned to version or git)
  mekari_network:
    git:
      url: https://bitbucket.org/mekari/mekari_network.git
      ref: <commit-hash>

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.12
  freezed: ^2.5.7
  json_serializable: ^6.8.0
  flutter_gen_runner: ^5.4.0
  mockito: ^5.4.4
  bloc_test: ^9.1.7
```

Feature package `pubspec.yaml` example:
```yaml
# features/crm_company/pubspec.yaml
name: crm_company

dependencies:
  flutter:
    sdk: flutter
  crm_core:
    path: ../crm_core
  qontak_common:
    path: ../qontak_common

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.12
  freezed: ^2.5.7
  json_serializable: ^6.8.0
  mockito: ^5.4.4
  bloc_test: ^9.1.7
```

**Rules:**
- Feature packages are local path dependencies — not pub packages
- Internal Mekari packages (`mekari_network`, etc.) are git dependencies pinned to a commit hash — never a branch
- Do NOT use `injectable_generator` — no code-gen DI

---

## Melos Configuration <!-- 12 -->

```yaml
# melos.yaml
name: qontak_crm_workspace

packages:
  - features/**

scripts:
  test:
    run: melos exec -- flutter test
    packageFilters:
      dirExists:
        - test
  gen:
    run: melos exec -- dart run build_runner build --delete-conflicting-outputs
    packageFilters:
      dependsOn:
        - build_runner
```

Run `melos bootstrap` after cloning — this links all local path packages.

---

## Linter Setup <!-- 8 -->

```yaml
# analysis_options.yaml (root and each feature package)
include: package:linter_rules/analysis_options.yaml  # Mekari Linter

analyzer:
  exclude:
    - '**/*.g.dart'
    - '**/*.freezed.dart'
    - '**/*.mocks.dart'
    - '**/objectbox.g.dart'
    - '**/l10n/**'
    - '**/gen/**'
```
