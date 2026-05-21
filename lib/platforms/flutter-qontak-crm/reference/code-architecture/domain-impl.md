# Flutter Qontak CRM — Domain Layer

> Concepts and invariants: `lib/core/reference/code-architecture/domain-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

Domain lives inside each feature package at `features/<pkg>/lib/src/domain/`. It has zero dependencies on data or presentation packages.

---

## Dependency Rule <!-- 15 -->

Domain is the innermost layer — it imports nothing from outer layers.

**Allowed:** `dart:core`, `package:freezed_annotation`, `package:fpdart` (for `Either`), `package:qontak_common` (re-exports `UseCase`, `Either`, `Failure`, `NoParams`).

**Forbidden:**

- `package:mekari_network` / `package:dio` — HTTP clients belong in data
- `package:flutter/material.dart` or any Flutter UI package — domain must be pure Dart
- Any BLoC, Cubit, or state-management import (`package:flutter_bloc`, `package:bloc`)
- Any data-layer import — no `*Response`, `*Request`, `*Db`, `*DataSource`, or `*RepositoryImpl` types
- Cross-module domain types must be imported through the module's public API (`package:<pkg>/<pkg>.dart`), never via relative paths across package boundaries

---

## Entities <!-- 30 -->

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

## Entity Semantic Quality Rules <!-- 38 -->

Before writing any entity field, work through these five questions. A field is only correct when all five have satisfactory answers.

**1. Type question**
Is this the most semantically precise type for this concept? Applies to every type — `String`, `int`, `double`, `List<X>`, `Map<K,V>`, `dynamic`. A date is `DateTime`, a status is a typed enum, a tag list is `List<Tag>` not `List<String>`. If the precise type does not exist yet, create it before writing the field.

**2. Origin question**
Where does this value come from? If the answer is "the API returns it as-is", that is a mapper failure — the mapper transforms wire types into domain types before they reach the entity.

**3. Ownership question**
Who sets this value after the entity is constructed? If it is set by user interaction on a screen (a tap, a toggle, a selection), it belongs in BLoC state. If it is set by the sync/network layer, answer question 1 first.

**4. Cardinality question**
For relationship fields: is this relation fixed-arity (zero-or-one, domain-defined at compile time) or open/backend-configurable (zero-to-many, cardinality controlled by server config)? Fixed-arity → named nullable field. Open/backend-driven → `List<TypedValueObject>`. The wrong choice creates unnecessary complexity or prevents future extensibility.

**5. Vocabulary unification question**
If this entity unifies two or more data sources, do any fields or enum values represent the same real-world concept under different API names? If yes, pick one canonical domain term — the entity must have no trace of which API coined it. Both mappers translate to the canonical term. Example: CRM API calls it `person`, CDP API calls it `contact` — the entity uses one term; both mappers produce it.

### Domain Type Vocabulary

Before writing any field type, check if a more precise type already exists.

**Step 1 — RAG query (primary):**

```
search_code("<concept> enum value object", project_slug="crm")
```

Returns existing enums, value objects, and typed IDs from live indexed Dartdoc. If a matching type is returned, use it.

**Step 2 — Grep fallback:**
If RAG is unavailable or empty: `Grep` for the concept term in `features/*/lib/src/domain/`. Create a new type only if both confirm it does not exist.

---

## Read Models (Page Data Aggregates) <!-- 22 -->

A Read Model is a data class that combines the results of two or more domain entities into a single aggregate needed by one screen. It is the return type of a Page Init UseCase.

**Rules:**

- Naming: `<Screen>PageData` (e.g. `CompanyDetailPageData`, `ContactDetailPageData`)
- Location: `features/<prefix>_<feature>/lib/src/domain/read_models/<screen>_page_data.dart`
- Implementation: `@freezed` class — same style as an entity, but contains entity references, not raw fields
- Imports: domain entities only — no DTOs, no BLoC types
- Read models are immutable; they are never updated after construction
- Do NOT create a Read Model for a screen that only needs one entity — use the entity directly

```dart
// features/crm_company/lib/src/domain/read_models/company_detail_page_data.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import '../entities/company.dart';
import '../entities/contact.dart';

part 'company_detail_page_data.freezed.dart';

@freezed
class CompanyDetailPageData with _$CompanyDetailPageData {
  const factory CompanyDetailPageData({
    required Company company,
    required List<Contact> contacts,
  }) = _CompanyDetailPageData;
}
```

---

## Repository Interfaces <!-- 26 -->

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

## Use Cases <!-- 67 -->

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

## Domain Services <!-- 22 -->

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

## Creation Order <!-- 10 -->

```
1. features/<pkg>/lib/src/domain/entities/<concept>.dart         ← Entity (@freezed, no fromJson)
2. features/<pkg>/lib/src/domain/repositories/<feature>_repository.dart ← Repository abstract class
3. features/<pkg>/lib/src/domain/usecases/<verb>_<concept>_usecase.dart ← Use Case(s) (callable)
4. features/<pkg>/lib/src/domain/services/<concept>_<noun>.dart  ← Domain Service (only if needed)
```

Never create a use case before the repository abstract class it depends on.
