# Flutter Qontak — Project Flavors

---

## Flavor Definitions <!-- 14 -->

Three standard flavors controlled by a `--dart-define` value:

| Flavor | `EnvType` | `DartDefine.env` value |
|---|---|---|
| Production | `EnvType.production` | `'PROD'` |
| Staging | `EnvType.staging` | `'STAGING'` (default) |
| Sandbox | `EnvType.sandbox` | `'SANDBOX'` |

---

## Dart Define — Env Selection <!-- 22 -->

No `.env` files or `envied` — env selection uses `String.fromEnvironment` at compile time:

```dart
// lib/config/constants/dart_define.dart
abstract class DartDefine {
  static const env = 'ENV';
  static const envProd = 'PROD';
  static const envStg = 'STAGING';
  static const envSbx = 'SANDBOX';
}

// lib/config/environment/env_type.dart
enum EnvType {
  production('prod'),
  staging('staging'),
  sandbox('sandbox');

  const EnvType(this.value);
  final String value;
}

EnvType determineEnvType(String input) {
  final lowerCaseInput = input.toLowerCase();
  for (final env in EnvType.values) {
    if (env.value.toLowerCase() == lowerCaseInput) return env;
  }
  return EnvType.staging; // default
}

// lib/engine.dart — reads at startup
EnvType getEnvType() {
  const readEnv = String.fromEnvironment(
    DartDefine.env,
    defaultValue: DartDefine.envStg,
  );
  return determineEnvType(readEnv);
}
```

---

## EnvData — Per-Flavor Config <!-- 22 -->

Environment-specific URLs and API keys are in concrete `EnvData` subclasses. The `Env` class selects the correct data at runtime.

```dart
// lib/config/environment/data/env_data.dart
abstract class EnvData {
  late String apiBaseUrl;
  late String ssoClientId;
  late String flagSmithApi;
  late String moengageWorkspaceId;
  late String mkrLogAuth;
  late String mkrLogBaseUrl;
  late String mkrLogEncryptionKey;
  late String chatBotBaseUrl;
  late String mixpanelToken;
  late String googleMapsApi;
  late String mqttBaseUrl;
  late String callApiBaseUrl;
  late String voiceApiBaseUrl;
  late String ssoUrl;
  late String customerBaseUrl;
  late String launchpadBaseUrl;
}

// lib/config/environment/env.dart
class Env {
  Env({EnvType? envType}) {
    if (envType != null) setAdaptive(envType: envType);
  }

  late EnvType type;
  late EnvData data;

  Future<void> setAdaptive({required EnvType envType}) async {
    switch (envType) {
      case EnvType.production: return setProduction();
      default: return setStaging();
    }
  }

  void setProduction() { type = EnvType.production; data = EnvProductionData(); }
  void setStaging()    { type = EnvType.staging;    data = EnvStagingData(); }

  bool get isProduction => type == EnvType.production;
  static bool get isDevMode => kDebugMode;
}
```

---

## Running Per Flavor <!-- 14 -->

```bash
# Staging (default)
flutter run

# Staging explicit
flutter run --dart-define=ENV=STAGING

# Production
flutter run --dart-define=ENV=PROD

# Sandbox
flutter run --dart-define=ENV=SANDBOX
```

---

## Firebase Per Flavor <!-- 16 -->

Each flavor maps to a separate Firebase project:

```
android/app/
├── google-services-production.json   → prod Firebase project
├── google-services-staging.json      → staging Firebase project
└── src/
    ├── production/google-services.json  (symlink or CI-injected)
    └── staging/google-services.json

ios/
├── config/
│   ├── firebase_options_prod.dart    ← lib/config/firebase/firebase_options_prod.dart
│   └── firebase_options_staging.dart
```

Firebase is initialized in `engine.dart` unconditionally:
```dart
if (Firebase.apps.isEmpty) await Firebase.initializeApp();
```

Use a CI pipeline or `Makefile` to inject the correct `google-services.json` and `GoogleService-Info.plist` per build target. Never commit real keys.
