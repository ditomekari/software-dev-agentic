# Flutter — Domain Layer

> Concepts and invariants: `reference/code-architecture/domain-theory.md`. This file covers Dart syntax and Flutter-specific patterns.

## Entities <!-- 30 -->

Immutable business objects with `@freezed`. **No `fromJson` — ever.**

```dart
// domain/entities/employee_entity.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'employee_entity.freezed.dart';

@freezed
class EmployeeEntity with _$EmployeeEntity {
  const factory EmployeeEntity({
    required String id,
    required String name,
    required String email,
    DateTime? joinDate,
  }) = _EmployeeEntity;
}
```

**Rules:**
- `@freezed` for immutability + `copyWith`
- Only `.freezed.dart` part — never `.g.dart`
- No `@JsonKey` annotations
- No `fromJson` / `toJson` factories
- Represent business concepts, not API shapes

---

## Repository Interfaces <!-- 32 -->

```dart
// domain/repositories/employee_repository.dart
import 'package:fpdart/fpdart.dart';
import '../entities/employee_entity.dart';
import '../errors/failure.dart';

abstract class EmployeeRepository {
  Future<Either<Failure, EmployeeEntity>> getEmployee(String id);
  Future<Either<Failure, List<EmployeeEntity>>> getEmployees({
    int page = 1,
    int limit = 20,
    String? departmentId,
  });
  Future<Either<Failure, EmployeeEntity>> updateEmployee(
    String id,
    UpdateEmployeeParams params,
  );
  Future<Either<Failure, void>> deleteEmployee(String id);
}
```

**Rules:**
- `abstract class` (not `interface` or `mixin`)
- Return `Either<Failure, T>` — never throw from a repository
- Return domain entities, never DTOs
- Method names follow REST: `get*`, `create*`, `update*`, `delete*`
- Params are domain objects, not raw `Map<String, dynamic>`

---

## Use Cases <!-- 145 -->

### UseCase Base Class

```dart
// domain/usecases/use_case.dart
import 'package:fpdart/fpdart.dart';
import '../errors/failure.dart';

abstract class UseCase<Type, Params> {
  Future<Either<Failure, Type>> call(Params params);
}

/// Use when no input parameters are needed.
class NoParams {
  const NoParams();
}
```

### GET — Single Item

```dart
// domain/usecases/employee/get_employee_usecase.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import '../../entities/employee_entity.dart';
import '../../errors/failure.dart';
import '../../repositories/employee_repository.dart';
import '../use_case.dart';

@lazySingleton
class GetEmployeeUseCase implements UseCase<EmployeeEntity, String> {
  GetEmployeeUseCase({required this.repository});

  final EmployeeRepository repository;

  @override
  Future<Either<Failure, EmployeeEntity>> call(String id) =>
      repository.getEmployee(id);
}
```

### GET — List with Params

```dart
// domain/usecases/employee/get_employees_usecase.dart
@lazySingleton
class GetEmployeesUseCase
    implements UseCase<List<EmployeeEntity>, GetEmployeesParams> {
  GetEmployeesUseCase({required this.repository});

  final EmployeeRepository repository;

  @override
  Future<Either<Failure, List<EmployeeEntity>>> call(
    GetEmployeesParams params,
  ) =>
      repository.getEmployees(
        page: params.page,
        limit: params.limit,
        departmentId: params.departmentId,
      );
}

class GetEmployeesParams {
  const GetEmployeesParams({
    this.page = 1,
    this.limit = 20,
    this.departmentId,
  });

  final int page;
  final int limit;
  final String? departmentId;
}
```

### POST/PUT — Write with Params

Params class wraps domain inputs. The Data layer converts to a Payload for serialization.

```dart
// domain/usecases/employee/update_employee_usecase.dart
@lazySingleton
class UpdateEmployeeUseCase
    implements UseCase<EmployeeEntity, UpdateEmployeeParams> {
  UpdateEmployeeUseCase({required this.repository});

  final EmployeeRepository repository;

  @override
  Future<Either<Failure, EmployeeEntity>> call(
    UpdateEmployeeParams params,
  ) =>
      repository.updateEmployee(params.id, params);
}

/// Pure Dart class — no freezed, no @JsonKey.
class UpdateEmployeeParams {
  const UpdateEmployeeParams({
    required this.id,
    required this.name,
    required this.email,
    this.departmentId,
  });

  final String id;
  final String name;
  final String email;
  final String? departmentId;
}
```

### No-Params Use Case

```dart
// domain/usecases/auth/get_current_user_usecase.dart
@lazySingleton
class GetCurrentUserUseCase
    implements UseCase<EmployeeEntity, NoParams> {
  GetCurrentUserUseCase({required this.repository});

  final AuthRepository repository;

  @override
  Future<Either<Failure, EmployeeEntity>> call(NoParams _) =>
      repository.getCurrentUser();
}
```

**Params naming summary:**

| HTTP | Params structure |
|------|-----------------|
| GET (single) | Use a plain `String` or typed ID |
| GET (list) | `XxxParams { page, limit, filters... }` |
| POST | `XxxParams { field1, field2... }` (pure Dart) |
| PUT | `XxxParams { id, field1... }` (pure Dart) |
| DELETE | Use a plain `String` ID |
| No input | `NoParams` |

**Naming:** `[Verb][Feature]UseCase` — `GetEmployeeUseCase`, `UpdateAttendanceUseCase`, `SubmitLeaveRequestUseCase`

---

## Domain Services <!-- 42 -->

Pure synchronous functions — no I/O, no async, no side effects. See extraction rules in `reference/code-architecture/domain-theory.md`.

```dart
// domain/services/leave_balance_calculator.dart
import '../entities/leave_entitlement_entity.dart';

class LeaveBalanceCalculator {
  int remainingDays(LeaveEntitlementEntity entitlement) {
    final pendingDays = entitlement.pendingRequests
        .where((r) => r.status == LeaveStatus.pending)
        .fold(0, (sum, r) => sum + r.days);
    final remaining =
        entitlement.annualDays - entitlement.usedDays - pendingDays;
    return remaining < 0 ? 0 : remaining;
  }

  bool isSufficient(
    LeaveEntitlementEntity entitlement,
    int requestedDays,
  ) =>
      remainingDays(entitlement) >= requestedDays;
}
```

**Rules:**
- No `@injectable` unless dependencies need to be injected
- Returns structured data — never formatted strings, CSS classes, or display text
- Presentation layer formats service output for display

**When to extract to a service:**

| Scenario | Action |
|----------|--------|
| 1-3 line condition | Keep inline in use case |
| Complex multi-step validation | Service |
| Reused by ≥ 2 use cases | Service |
| Needs unit testing in isolation | Service |

---

## Domain Errors <!-- 46 -->

The unified error type returned from all repository and use case calls.

```dart
// domain/errors/failure.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'failure.freezed.dart';

@freezed
abstract class Failure<T> with _$Failure<T> {
  /// API returned an error status.
  factory Failure.serverFailure({
    required String message,
    required String developerMessage,
    int? statusCode,
    String? errorCode,
  }) = ServerFailure;

  /// API returned validation errors keyed by field.
  factory Failure.validationFailure({
    required String message,
    T? errors,
    int? statusCode,
  }) = ValidationFailure<T>;

  /// No internet connection or DNS failure.
  factory Failure.networkFailure({
    required String message,
  }) = NetworkFailure;

  /// Unexpected error (bug, null response, parse error).
  factory Failure.unknownFailure({
    required String message,
  }) = UnknownFailure;

  /// Local storage read/write failure.
  factory Failure.localFailure({
    required String message,
  }) = LocalFailure;
}
```

---

## Domain Enums <!-- 20 -->

Business-level constants. Place in `domain/enums/`.

```dart
// domain/enums/leave_status.dart
enum LeaveStatus {
  pending,
  approved,
  rejected,
  cancelled;

  bool get isTerminal =>
      this == approved || this == rejected || this == cancelled;
}
```

**Rules:**
- Raw `String` values only when needed for direct API mapping
- No UI strings — display formatting belongs in presentation
