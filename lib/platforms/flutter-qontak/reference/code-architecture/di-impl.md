# Flutter Modular — Dependency Injection

> Single-package DI patterns: `../../flutter/reference/code-architecture/di-impl.md`.
> This file covers per-module DI with Injectable MicroPackages.

---

## Per-Module DI Setup <!-- 56 -->

Each module has its own `@module` class and initializes its own Injectable
container. The application module aggregates all modules at startup.

### Feature Module DI

```dart
// features/[prefix]_auth/lib/src/configs/auth_di.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

import 'auth_di.config.dart';  // ← generated

final _authGetIt = GetIt.asNewInstance();

@InjectableInit(
  initializerName: 'initAuthDependencies',
  preferRelativeImports: true,
  asExtension: false,
)
Future<void> initAuthDependencies() => _authGetIt.init(initAuthDependencies);
```

Annotate all classes in the feature with `@injectable`, `@lazySingleton`, etc.
They are discovered automatically by `build_runner`.

### Application Module — Aggregate Registration

```dart
// lib/configs/di/injection.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

import 'package:[prefix]_auth/src/configs/auth_di.dart';
import 'package:[prefix]_inbox/src/configs/inbox_di.dart';

import 'injection.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async {
  // Register module-level dependencies first
  await initAuthDependencies();
  await initInboxDependencies();

  // Then register app-level dependencies
  await getIt.init();
}
```

Call `configureDependencies()` in `main.dart` before `runApp`.

---

## Module API Registration <!-- 16 -->

Module API implementations must be registered in their owning module's DI:

```dart
// features/[prefix]_employee/lib/src/module_api/employee_module_api_impl.dart
@LazySingleton(as: EmployeeModuleApi)
class EmployeeModuleApiImpl implements EmployeeModuleApi { ... }
```

`@LazySingleton(as: EmployeeModuleApi)` registers the concrete class under
the abstract type. Consumer features resolve `EmployeeModuleApi` from the
same `GetIt` instance without knowing the implementation.

---

## Registration Order Rules <!-- 9 -->

1. `[prefix]_dependencies` — no DI (just re-exports)
2. `[prefix]_core` — registers network client, logger, base utilities
3. Feature modules — register their own layers + Module API impls
4. Application module — registers app-level config; calls all above

---

## Scoping Rules <!-- 14 -->

| Annotation | When to use |
|---|---|
| `@lazySingleton` | Stateless services, repositories, data sources |
| `@singleton` | Stateful services that must init eagerly |
| `@injectable` | BLoCs, Cubits (new instance per injection) |
| `@LazySingleton(as: IFace)` | Module API implementations registered under their interface |

**Rule:** BLoCs are `@injectable` (not singleton). Every `BlocProvider` gets a
fresh instance so state doesn't leak across screen navigations.

---

## Code Generation <!-- 11 -->

```bash
# From workspace root (melos)
melos run build_runner

# Or per-package
cd features/[prefix]_auth && dart run build_runner build --delete-conflicting-outputs
```

Each module produces its own `*.config.dart` — never edit generated files.
