# Flutter Modular — Project Flavors

---

## Flavor Definitions <!-- 20 -->

Three standard flavors:

| Flavor | Android applicationId suffix | iOS bundleId suffix |
|---|---|---|
| `production` | _(none — base ID)_ | _(none — base ID)_ |
| `staging` | `.dev` | `.dev` |
| `sandbox` | `.sbx` | `.sbx` (optional) |

Example for base ID `com.mekari.qontak`:

| Flavor | Android | iOS |
|---|---|---|
| production | `com.mekari.qontak` | `com.mekari.qontak` |
| staging | `com.mekari.qontak.dev` | `com.mekari.qontak.dev` |
| sandbox | `com.mekari.qontak.sbx` | `com.mekari.qontak.sbx` |

---

## Dart Define — Env Variables <!-- 31 -->

Use `Envied` to load environment-specific config from `.env` files safely:

```dart
// lib/configs/env/app_env.dart
import 'package:envied/envied.dart';

part 'app_env.g.dart';

@Envied(path: '.env')
abstract class AppEnv {
  @EnviedField(varName: 'API_BASE_URL', obfuscate: true)
  static final String apiBaseUrl = _AppEnv.apiBaseUrl;

  @EnviedField(varName: 'FLAVOR')
  static final String flavor = _AppEnv.flavor;
}
```

`.env` files per flavor:
```
.env.production
.env.staging
.env.sandbox
```

Add all `.env` files to `.gitignore`. Provide `.env.example` for each.

---

## Running Per Flavor <!-- 16 -->

```bash
# Staging
flutter run --dart-define-from-file=.env.staging

# Production
flutter run --dart-define-from-file=.env.production

# Via melos script
melos run run:staging
melos run run:production
```

---

## Firebase Per Flavor <!-- 19 -->

Each flavor maps to a separate Firebase project:

```
android/app/
├── google-services-production.json   → prod Firebase project
├── google-services-staging.json      → staging Firebase project
└── src/
    ├── production/google-services.json  (symlink or CI-injected)
    └── staging/google-services.json

ios/
├── GoogleService-Info-Production.plist
└── GoogleService-Info-Staging.plist
```

Use a `Makefile` or melos script to copy the correct file before building.
Never commit `google-services.json` or `GoogleService-Info.plist` with real keys.
