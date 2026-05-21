# Flutter Qontak — Domain Layer

> Concepts and invariants: `lib/core/reference/code-architecture/domain-theory.md`. This file covers Dart syntax and patterns.

Domain lives inside each feature package at `lib/src/domain/`. It has zero dependencies on data or presentation packages.

---

## Dependency Rule <!-- 15 -->

Domain is the innermost layer — it imports nothing from outer layers.

**Allowed:** `dart:core`, `package:freezed_annotation`, `package:fpdart` (for `Either`), `package:[prefix]_core/[prefix]_core.dart` (re-exports `Failure` and `UseCase` base only).

**Forbidden:**

- `package:dio` / `package:http` — HTTP clients belong in data
- `package:flutter/material.dart` or any Flutter UI package — domain must be pure Dart
- Any BLoC, Cubit, or state-management import (`package:flutter_bloc`, `package:bloc`)
- Any data-layer import — no `*Response`, `*Request`, `*Db`, `*DataSource`, or `*RepositoryImpl` types
- Cross-module domain types must be imported through the module's public API (`package:[prefix]_[module]/[prefix]_[module].dart`), never via relative paths across package boundaries

---

## Entities <!-- 28 -->

```dart
// [prefix]_auth/lib/src/domain/entities/user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    required String email,
    DateTime? joinDate,
  }) = _User;
}
```

**Rules:**

- `@freezed` — immutability + `copyWith`
- Only `.freezed.dart` part — never `.g.dart`
- No `@JsonKey`, no `fromJson`, no `toJson`
- Named after the business concept, no `Entity` suffix (Confluence convention)
- All nullable DTO fields become non-null with defaults at the mapper boundary

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
If this entity unifies two or more data sources, do any fields or enum values represent the same real-world concept under different API names? If yes, pick one canonical domain term — the entity must have no trace of which API coined it. Both mappers translate to the canonical term.

### Domain Type Vocabulary

Before writing any field type, check if a more precise type already exists.

**Step 1 — RAG query (primary):**

```
search_code("<concept> enum value object", project_slug="chat")
```

Returns existing enums, value objects, and typed IDs from live indexed Dartdoc. If a matching type is returned, use it.

**Step 2 — Grep fallback:**
If RAG is unavailable or empty: `Grep` for the concept term in the domain directories. Create a new type only if both confirm it does not exist.

---

## Read Models (Page Data Aggregates) <!-- 22 -->

A Read Model is a data class that combines the results of two or more domain entities into a single aggregate needed by one screen. It is the return type of a Page Init UseCase.

**Rules:**

- Naming: `<Screen>PageData` (e.g. `RoomDetailPageData`, `InboxPageData`)
- Location: `features/<prefix>_<feature>/lib/src/domain/read_models/<screen>_page_data.dart`
- Implementation: `@freezed` class — same style as an entity, but contains entity references, not raw fields
- Imports: domain entities only — no DTOs, no BLoC types
- Read models are immutable; they are never updated after construction
- Do NOT create a Read Model for a screen that only needs one entity — use the entity directly

```dart
// features/chat_room/lib/src/domain/read_models/room_detail_page_data.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import '../entities/room.dart';
import '../entities/participant.dart';

part 'room_detail_page_data.freezed.dart';

@freezed
class RoomDetailPageData with _$RoomDetailPageData {
  const factory RoomDetailPageData({
    required Room room,
    required List<Participant> participants,
  }) = _RoomDetailPageData;
}
```

---

## Repository Interfaces <!-- 23 -->

```dart
// [prefix]_auth/lib/src/domain/repositories/auth_repository.dart
import 'package:fpdart/fpdart.dart';
import 'package:[prefix]_core/[prefix]_core.dart'; // re-exports Failure
import '../entities/user.dart';

abstract class AuthRepository {
  Future<Either<Failure, User>> login(String email, String password);
  Future<Either<Failure, User>> getCurrentUser();
  Future<Either<Failure, void>> logout();
}
```

**Rules:**

- `abstract class` — never `interface` or `mixin`
- Return `Either<Failure, T>` — never throw
- Return domain entities, not DTOs
- Repository interface belongs in domain; implementation in data

---

## Use Cases <!-- 64 -->

### Base Class (in `[prefix]_core`)

```dart
// shared/[prefix]_core/lib/src/base/use_case.dart
import 'package:fpdart/fpdart.dart';
import 'failure.dart';

abstract class UseCase<Type, Params> {
  Future<Either<Failure, Type>> call(Params params);
}

class NoParams {
  const NoParams();
}
```

### GET — Single Item

```dart
// [prefix]_auth/lib/src/domain/usecases/get_current_user.dart
import 'package:injectable/injectable.dart';
import 'package:[prefix]_core/[prefix]_core.dart';
import '../entities/user.dart';
import '../repositories/auth_repository.dart';

@lazySingleton
class GetCurrentUser implements UseCase<User, NoParams> {
  GetCurrentUser(this._repository);
  final AuthRepository _repository;

  @override
  Future<Either<Failure, User>> call(NoParams _) =>
      _repository.getCurrentUser();
}
```

### POST/PUT — Write with Params

```dart
// [prefix]_auth/lib/src/domain/usecases/login.dart
@lazySingleton
class Login implements UseCase<User, LoginParams> {
  Login(this._repository);
  final AuthRepository _repository;

  @override
  Future<Either<Failure, User>> call(LoginParams params) =>
      _repository.login(params.email, params.password);
}

class LoginParams {
  const LoginParams({required this.email, required this.password});
  final String email;
  final String password;
}
```

**Naming:** verb-only, no `UseCase` suffix (`Login`, `GetCurrentUser`, `SendMessage`).
Class is a callable: `useCase(params)` not `useCase.execute(params)`.

---

## Domain Services <!-- 20 -->

Pure synchronous logic. No I/O, no async, no side effects.

```dart
// [prefix]_auth/lib/src/domain/services/password_strength_checker.dart
class PasswordStrengthChecker {
  PasswordStrength check(String password) {
    if (password.length < 8) return PasswordStrength.weak;
    final hasUpper = password.contains(RegExp(r'[A-Z]'));
    final hasDigit = password.contains(RegExp(r'[0-9]'));
    return (hasUpper && hasDigit) ? PasswordStrength.strong : PasswordStrength.medium;
  }
}

enum PasswordStrength { weak, medium, strong }
```

---

## Failure (shared in `[prefix]_core`) <!-- 33 -->

```dart
// shared/[prefix]_core/lib/src/domain/failure.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'failure.freezed.dart';

@freezed
abstract class Failure<T> with _$Failure<T> {
  factory Failure.serverFailure({
    required String message,
    required String developerMessage,
    int? statusCode,
    String? errorCode,
  }) = ServerFailure;

  factory Failure.validationFailure({
    required String message,
    T? errors,
    int? statusCode,
  }) = ValidationFailure<T>;

  factory Failure.networkFailure({required String message}) = NetworkFailure;

  factory Failure.unknownFailure({required String message}) = UnknownFailure;

  factory Failure.localFailure({required String message}) = LocalFailure;
}
```

---

## Domain Enums <!-- 17 -->

```dart
// [prefix]_chat/lib/src/domain/enums/message_status.dart
enum MessageStatus {
  sending,
  sent,
  delivered,
  read,
  failed;

  bool get isTerminal => this == delivered || this == read || this == failed;
}
```

No UI strings in enums — display formatting belongs in presentation.

## Creation Order <!-- 17 -->

When building a new feature's domain layer, create files in this sequence:

```
1. [prefix]_[feature]/lib/src/domain/entities/[concept].dart
                                                     ← Entity (@freezed, no fromJson, no Entity suffix)
2. [prefix]_[feature]/lib/src/domain/repositories/[feature]_repository.dart
                                                     ← Repository abstract class
3. [prefix]_[feature]/lib/src/domain/usecases/[verb]_[concept].dart
   ...                                               ← Use Case(s) (callable, verb-only naming)
4. [prefix]_[feature]/lib/src/domain/services/[concept]_[checker|calculator].dart
                                                     ← Domain Service (only if needed)
```

Never create a use case before the repository abstract class it depends on.
Cross-module domain entities must be accessed via the exporting package's public API — never via relative paths.
