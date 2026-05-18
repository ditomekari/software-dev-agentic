# Flutter Qontak CRM — Domain Layer

> Concepts and invariants: `lib/core/reference/code-architecture/domain-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

Domain lives inside each feature package at `features/<pkg>/lib/src/domain/`. It has zero dependencies on data or presentation packages.

---

## Dependency Rule <!-- 13 -->

Domain is the innermost layer — it imports nothing from outer layers.

**Allowed:** `dart:core`, `package:freezed_annotation`, `package:fpdart` (for `Either`), `package:qontak_common` (re-exports `UseCase`, `Either`, `Failure`, `NoParams`).

**Forbidden:**
- `package:mekari_network` / `package:dio` — HTTP clients belong in data
- `package:flutter/material.dart` or any Flutter UI package — domain must be pure Dart
- Any BLoC, Cubit, or state-management import (`package:flutter_bloc`, `package:bloc`)
- Any data-layer import — no `*Response`, `*Request`, `*Db`, `*DataSource`, or `*RepositoryImpl` types
- Cross-module domain types must be imported through the module's public API (`package:<pkg>/<pkg>.dart`), never via relative paths across package boundaries

---

## Entities <!-- 18 -->

```dart
// features/crm_company/lib/src/domain/entities/company.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'company.freezed.dart'; // .freezed.dart only — never .g.dart

@freezed
class Company with _$Company {
  const factory Company({
    required String id,
    required String name,
    String? phone,
    DateTime? createdAt,
  }) = _Company;
  // no fromJson — entities are never deserialised from JSON
}
```

**Rules:**
- `@freezed` for immutability + `copyWith`
- Only `.freezed.dart` part — never `.g.dart`
- No `@JsonKey`, no `fromJson`, no `toJson`
- Named after the business concept — no `Entity` suffix
- All nullable DTO fields become non-null with defaults at the mapper boundary, not here
- Allowed imports: `dart:core`, `package:freezed_annotation`, `package:qontak_common` only

---

## Repository Interfaces <!-- 18 -->

```dart
// features/crm_company/lib/src/domain/repositories/company_repository.dart
import 'package:fpdart/fpdart.dart';
import 'package:qontak_common/qontak_common.dart'; // re-exports Failure
import '../entities/company.dart';

abstract class CompanyRepository {
  // all methods return Either<Failure, T> — never throw
  Future<Either<Failure, Company>> getCompany(String id);
  Future<Either<Failure, List<Company>>> getCompanyList();
  Future<Either<Failure, Company>> addCompany(String name, String phone);
  Future<Either<Failure, void>> deleteCompany(String id);
}
```

**Rules:**
- `abstract class` — never `interface` or `mixin`
- Return `Either<Failure, T>` — never throw
- Return domain entities, not DTOs (`CompanyResponse`)
- Repository interface belongs in domain; implementation belongs in data
- Import `Failure` from `package:qontak_common` — never from data or presentation

---

## Use Cases <!-- 35 -->

CRM use cases extend `UseCase<ReturnType, Params>` from `qontak_common` and carry the `UseCase` suffix.

### GET — Single Item

```dart
// features/crm_company/lib/src/domain/usecases/get_company_usecase.dart
import 'package:fpdart/fpdart.dart';
import 'package:qontak_common/qontak_common.dart'; // UseCase, NoParams, Failure
import '../entities/company.dart';
import '../repositories/company_repository.dart';

// No @lazySingleton — registration is manual in QontakCompanyDependency
class GetCompanyUseCase implements UseCase<Company, GetCompanyParams> {
  GetCompanyUseCase({required this.repository});
  final CompanyRepository repository;

  @override
  Future<Either<Failure, Company>> call(GetCompanyParams params) =>
      repository.getCompany(params.id);
}

class GetCompanyParams {
  const GetCompanyParams({required this.id});
  final String id;
}
```

### No Params

```dart
class GetCurrentUserUseCase implements UseCase<AuthToken, NoParams> {
  GetCurrentUserUseCase({required this.repository});
  final AuthRepository repository;

  @override
  Future<Either<Failure, AuthToken>> call(NoParams _) =>
      repository.getCurrentUser();
}
```

### Write (POST/PUT)

```dart
class AddCompanyUseCase implements UseCase<Company, AddCompanyParams> {
  AddCompanyUseCase({required this.repository});
  final CompanyRepository repository;

  @override
  Future<Either<Failure, Company>> call(AddCompanyParams params) =>
      repository.addCompany(params.name, params.phone);
}

class AddCompanyParams {
  const AddCompanyParams({required this.name, required this.phone});
  final String name;
  final String phone;
}
```

**Naming:** `<Verb><Entity>UseCase` WITH `UseCase` suffix (e.g. `GetCompanyUseCase`, `AddCompanyUseCase`, `DeleteCompanyUseCase`).
Class is callable: `useCase(params)` not `useCase.execute(params)`.
Params class: plain Dart, no `@freezed`, no `@JsonKey`.

---

## Domain Services <!-- 12 -->

Pure synchronous logic. No I/O, no async, no side effects.

```dart
// features/crm_deal/lib/src/domain/services/deal_stage_calculator.dart
import '../entities/deal.dart';
import '../enums/deal_stage.dart';

class DealStageCalculator {
  DealStage calculate(Deal deal) {
    if (deal.amount <= 0) return DealStage.prospect;
    if (deal.closedAt != null) return DealStage.closed;
    return DealStage.negotiation;
  }
}
```

**Rules:** No `async`, no I/O, returns structured data (enums, booleans, numbers) — never formatted display strings. Extract to a service only when logic is > 3 lines complex, reused by ≥ 2 use cases, or needs isolated testing.

---

## Creation Order <!-- 8 -->

```
1. features/<pkg>/lib/src/domain/entities/<concept>.dart         ← Entity (@freezed, no fromJson)
2. features/<pkg>/lib/src/domain/repositories/<feature>_repository.dart ← Repository abstract class
3. features/<pkg>/lib/src/domain/usecases/<verb>_<concept>_usecase.dart ← Use Case(s) (callable)
4. features/<pkg>/lib/src/domain/services/<concept>_<noun>.dart  ← Domain Service (only if needed)
```

Never create a use case before the repository abstract class it depends on.
