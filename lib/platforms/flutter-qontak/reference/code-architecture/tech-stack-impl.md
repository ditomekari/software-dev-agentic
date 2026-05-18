# Flutter Modular — Tech Stack

Standard dependencies for Mekari/Qontak Flutter modular projects.

---

## Core Dependencies <!-- 24 -->

| Purpose | Package | Notes |
|---|---|---|
| State Management | `flutter_bloc` | Preferred for predictability at scale; used across all Mekari Flutter projects |
| Environment | `envied` | Obfuscates `.env` values; avoids secrets in compiled binary |
| Localization | Flutter SDK `flutter_localizations` | Official; per-feature `.arb` files (see localization-impl.md) |
| Navigation | `go_router` | Declarative, Navigator 2.0, deep linking, nested routes, redirect |
| Immutable Models | `freezed` + `freezed_annotation` | `copyWith`, sealed classes, pattern matching |
| JSON Serialization | `json_annotation` + `json_serializable` | Use with `freezed` for DTO models |
| Local Storage | `isar` | High-performance NoSQL; supports modular architecture |
| Dependency Injection | `get_it` + `injectable` | `get_it` is the locator; `injectable` generates boilerplate; MicroPackages for per-module init |
| Logging | `logger` | Simple, extensible; development only — disable in production builds |
| Analytics | `firebase_analytics` | User behavior and engagement tracking |
| Crash Reporting | `firebase_crashlytics` | Monitor and triage crashes |
| Networking | Mekari Network (internal) | Wraps `dio`; centralized interceptors, auth token refresh |
| Authentication | Mekari Auth (internal) | Mekari Secure Id (MSI) integration |
| Design System | Mekari Pixel (internal) | Reusable UI components aligned to Mekari design system |
| Asset Generation | `flutter_gen` | Type-safe access to images, fonts, colors |
| Unit Test Mocking | `mockito` | Code-gen mocks via `@GenerateMocks` |
| BLoC Testing | `bloc_test` | `blocTest()`, `whenListen()` for BLoC/Cubit unit tests |

---

## pubspec.yaml Patterns <!-- 34 -->

Feature modules reference shared packages from local paths:

```yaml
# features/[prefix]_auth/pubspec.yaml
name: [prefix]_auth

dependencies:
  flutter:
    sdk: flutter
  [prefix]_core:
    path: ../../shared/[prefix]_core
  [prefix]_dependencies:
    path: ../../shared/[prefix]_dependencies

dev_dependencies:
  build_runner: ^2.4.12
  freezed: ^2.5.7
  injectable_generator: ^2.6.2
  json_serializable: ^6.8.0
  mockito: ^5.4.4
  bloc_test: ^9.1.7
```

**Rules:**
- All third-party packages installed in `[prefix]_dependencies`; feature modules
  access them through it.
- Do NOT add direct `flutter_bloc`, `go_router`, etc. to feature `pubspec.yaml`.
- For external Mekari modules shared across Flutter apps, pin to a git tag or
  commit hash — never a branch.

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
