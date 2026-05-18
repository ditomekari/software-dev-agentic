# Flutter Modular — Localization

---

## Per-Feature .arb Files <!-- 41 -->

Each feature module manages its own translations. Never add feature-specific
keys to a shared or app-level `.arb` file.

```
features/[prefix]_auth/
└── assets/
    └── l10n/
        ├── auth_en.arb
        └── auth_id.arb
```

`.arb` file naming: `[feature]_[locale].arb`

```json
// features/[prefix]_auth/assets/l10n/auth_en.arb
{
  "@@locale": "en",
  "loginTitle": "Sign In",
  "loginEmailLabel": "Email address",
  "loginPasswordLabel": "Password",
  "loginSubmitButton": "Sign In",
  "loginErrorInvalidCredentials": "Invalid email or password.",
  "loginForgotPassword": "Forgot password?",
  "welcomeUser": "Welcome, {name}!",
  "@welcomeUser": {
    "placeholders": {
      "name": { "type": "String" }
    }
  }
}
```

**Rules:**
- Use the feature name as prefix for every key (`loginTitle`, not `title`).
- Use placeholders (`{name}`) for dynamic values — never string concatenation.
- Add `@@locale` to every `.arb` file.

---

## l10n.yaml Per Module <!-- 17 -->

```yaml
# features/[prefix]_auth/l10n.yaml
arb-dir: assets/l10n
template-arb-file: auth_en.arb
output-localization-file: auth_localizations.dart
output-class: AuthLocalizations
output-dir: lib/src/gen/l10n
nullable-getter: false
```

Generated output lands in `lib/src/gen/l10n/` — add to `.gitignore` or commit
(choose one policy per project).

---

## Exposing LocalizationsDelegate <!-- 30 -->

```dart
// features/[prefix]_auth/lib/src/configs/auth_module.dart
import '../gen/l10n/auth_localizations.dart';

class AuthModule implements BaseModule {
  @override
  LocalizationsDelegate<dynamic>? localizationsDelegate() =>
      AuthLocalizations.delegate;
  // ...
}
```

`ModuleRegistrar` collects all delegates and passes them to `MaterialApp`:

```dart
MaterialApp.router(
  localizationsDelegates: [
    ...ModuleRegistrar.localizationDelegates,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  supportedLocales: const [Locale('en'), Locale('id')],
)
```

---

## Unlocalized Text Extension <!-- 15 -->

Mark strings that are not yet translated to track them:

```dart
// shared/[prefix]_core/lib/src/utils/string_ext.dart
extension UnlocalizedString on String {
  String get unlocalized => this; // intentionally untranslated
}

// Usage
'Debug only label'.unlocalized
```

This makes it easy to grep for untranslated strings: `Grep "\.unlocalized"`.
