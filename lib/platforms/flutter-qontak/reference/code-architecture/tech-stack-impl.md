# Flutter Modular — Tech Stack

Standard dependencies for Mekari/Qontak Flutter modular projects.

---

## Core Dependencies <!-- 26 -->

| Purpose | Package | Notes |
|---|---|---|
| State Management | `flutter_bloc` | Preferred for predictability at scale; used across all Mekari Flutter projects |
| Environment | `String.fromEnvironment` (SDK) | `DartDefine` constants + `EnvType`/`EnvData` classes — no `envied` |
| Localization | Flutter SDK `flutter_localizations` | Official; per-feature `.arb` files (see localization-impl.md) |
| Navigation | Flutter SDK `Navigator` 1.0 | `MaterialPageRoute` + `NavigationHelper`/`NavigationHelperImpl` — no `go_router` |
| Immutable Models | `freezed` + `freezed_annotation` | `copyWith`, sealed classes, pattern matching |
| JSON Serialization | `json_annotation` + `json_serializable` | Use with `freezed` for DTO models |
| Local Storage | `shared_preferences` | Used via `ChatPrefHelper`; Isar used for DB schemas (via `qontak_common.DatabaseService`) |
| Dependency Injection | `get_it` (manual) | No `injectable`/code generation in app module — manual `registerFactory`/`registerLazySingleton` |
| Analytics | `firebase_analytics` | User behavior and engagement tracking |
| Crash Reporting | `firebase_crashlytics` | Monitor and triage crashes; wired in `engine.dart` |
| Analytics (Mobile) | `moengage_flutter`, `mixpanel_flutter` | MoEngage + Mixpanel for mobile event tracking |
| Networking | MKRNetwork (internal) | Wraps `dio`; centralized interceptors, auth token refresh |
| Authentication | Bricks SDK (internal) | Auth flow orchestration via `Bricks.init()` with `AuthModule` |
| Design System | Qontak Component Library (internal) | Reusable UI components |
| Feature Flags | `qontak_common.FeatureFlagHelper` + MKRFlagFirebaseProvider | Remote config via Firebase + local seed defaults |
| Logging | `qontak_common.MkrLogHelper` (internal) | MKRLog with Firebase Crashlytics integration |
| Unit Test Mocking | `mockito` | Code-gen mocks via `@GenerateNiceMocks` |
| BLoC Testing | `bloc_test` | `blocTest()`, `whenListen()` for BLoC/Cubit unit tests |

---

## pubspec.yaml Patterns <!-- 28 -->

The application module (`qontak_chat_app`) declares feature packages as pub dependencies (not local paths — they are external packages):

```yaml
# pubspec.yaml (application module)
name: qontak_chat_app

dependencies:
  flutter:
    sdk: flutter
  chat_core:          # core + qontak_common re-exported
  chat_inbox:
  chat_messaging:
  chat_conversation:
  chat_contact:
  chat_call:
  chat_composer:
  qontak_user_management:
  # ... other internal packages pinned to version/git

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
- Feature packages (`chat_*`) are external pub dependencies — not local path packages.
- `qontak_common` is accessed via re-exports from `chat_core` (`import 'package:chat_core/qontak_common.dart'`).
- For internal Mekari packages, pin to a specific version or git commit — never a branch.
- Do NOT use `injectable_generator` — no code-gen DI in the app module.

---

## Linter Setup <!-- 19 -->

```yaml
# analysis_options.yaml (root workspace and each package)
include: package:linter_rules/analysis_options.yaml  # Mekari Linter
# or fallback:
# include: package:flutter_lints/flutter.yaml

analyzer:
  exclude:
    - '**/*.g.dart'
    - '**/*.freezed.dart'
    - '**/*.mocks.dart'
    - '**/injection.config.dart'
    - '**/l10n/**'
```

The Mekari Linter rule set is added as a git submodule (`linter-rules/`).
Reference it with a relative path in `analysis_options.yaml`.
