# Flutter Qontak — Domain Layer

> Concepts and invariants: `lib/core/reference/code-architecture/domain-theory.md`. This file covers Dart syntax and patterns.

Domain lives inside each feature package at `lib/src/domain/`. It has zero dependencies on data or presentation packages.

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

## Domain Enums <!-- 16 -->

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
