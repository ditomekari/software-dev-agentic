# Flutter Qontak CRM — Syntax Conventions

> Concepts and invariants: `lib/core/reference/code-architecture/syntax-conventions-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

---

## Naming Conventions <!-- 28 -->

| Artifact | Convention | Example |
|---|---|---|
| Feature package | `crm_<domain>` or `qontak_<domain>` | `crm_company`, `qontak_custom_form` |
| Domain entity | PascalCase, no suffix | `Company`, `AuthToken` |
| Remote model (app root) | `<Name>Model` | `AuthTokenModel` |
| Remote model (feature) | `<Name>Response` / `<Name>Request` | `CompanyResponse`, `CompanyFilterRequest` |
| Local/DB model (Isar) | `<Name>Db` | `CompanyDb` |
| Local/DB model (ObjectBox) | `<Name>ObjectBox` | `CompanyObjectBox` |
| Use case | `<Verb><Entity>UseCase` | `GetCompanyByIdUseCase`, `AddCompanyUseCase` |
| Repository interface | `<Entity>Repository` | `CompanyRepository` |
| Repository impl | `<Entity>RepositoryImpl` | `CompanyRepositoryImpl` |
| Remote data source | `<Entity>RemoteDataSource` + `Impl` | `CompanyRemoteDataSource` |
| Local data source | `<Entity>LocalDataSource` + `Impl` | `CompanyDataLocalDataSource` |
| BLoC | `<Feature>Bloc` | `CompanyBloc`, `LoginBloc` |
| BLoC event | `<Feature>Event` (freezed union) | `CompanyEvent` |
| BLoC state | `<Feature>State` (freezed) | `CompanyState` |
| DI class | `Qontak<Feature>Dependency` | `QontakCompanyDependency` |
| DI accessor | `qontak<Feature>Dependency` | `qontakCompanyDependency` |
| Mapper (feature) | `<Feature>Mapper` | `CompanyMapper` |
| Mapper (app root) | `CrmMapper<Source>To<Target>` | `CrmMapperModelToEntity` |
| Screen | `<Name>Screen` | `CompanyScreen`, `LoginScreen` |
| Screen arguments | `<Name>Argument` | `LoginScreenArgument` |
| Module class | `<PREFIX>Module` | `CRMCompanyModule`, `QontakCommonModule` |
| Endpoint constants | `Endpoint.<name>` static | `Endpoint.company`, `Endpoint.login` |

---

## File Placement Rules <!-- 15 -->

| What | Where |
|---|---|
| New feature package | `features/<crm_or_qontak>_<domain>/` |
| Feature public export | `features/<pkg>/lib/<pkg>.dart` |
| Feature internal source | `features/<pkg>/lib/src/` |
| App-shell BLoC | `lib/presentation/bloc/<feature>/` |
| App-shell screen | `lib/presentation/screens/<feature>/` |
| App-level entity | `lib/domain/entities/<name>/` |
| App-level use case | `lib/domain/usecases/<name>_usecase.dart` |
| App-level remote model | `lib/data/models/<name>/<name>_model.dart` |
| App-level repository impl | `lib/data/repositories/<name>_repository_impl.dart` |
| App-level DI | `lib/configs/di/qontak_crm_dependency.dart` |
| Endpoint constants | `lib/configs/constants/endpoint.dart` (app) or `lib/src/config/constants/endpoint.dart` (feature) |
| Generated assets | `lib/gen/assets/` (managed by flutter_gen — do not edit) |
| Generated l10n | `lib/gen/l10n/` (managed by flutter_localizations — do not edit) |

---

## Import Order <!-- 10 -->

```dart
// 1. Dart SDK
import 'dart:async';

// 2. Flutter
import 'package:flutter/material.dart';

// 3. External packages (alphabetical)
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:qontak_common/qontak_common.dart';

// 4. Internal packages (alphabetical)
import 'package:crm_core/crm_core.dart';

// 5. Relative imports (same package)
import '../entities/company.dart';
import '../repositories/company_repository.dart';
```

---

## Null Safety Patterns <!-- 12 -->

```dart
// Prefer ?? with explicit defaults in mapper
final name = response.name ?? '';
final count = response.count ?? 0;

// Use ?.let / ?.map for optional chaining
final date = response.createdAt != null
    ? DateTime.tryParse(response.createdAt!)
    : null;

// Never use ! in domain entities — guarantee non-null at mapper boundary
// Entity fields are non-null; DTO fields are nullable
```

---

## Code Style <!-- 10 -->

- `const` constructors wherever possible
- `final` for all injected dependencies in class fields
- Named parameters for constructors with ≥ 2 params
- `required` keyword on mandatory named params — no nullable workarounds
- No `dynamic` except in JSON deserialization
- No `late` except for BLoC initialization in `StatefulWidget.initState`
- `part of` for BLoC event/state files — they belong to the bloc file's namespace

---

## Linter Setup <!-- 10 -->

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
```

The Mekari Linter rule set is referenced from the root. Each feature package's `analysis_options.yaml` includes it.
