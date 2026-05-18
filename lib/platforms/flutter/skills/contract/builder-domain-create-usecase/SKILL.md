---
name: builder-domain-create-usecase
description: Create a UseCase class for a single business operation, with its Params class.
user-invocable: false
---

Create a UseCase following `.claude/reference/code-architecture/domain-impl.md ## Use Cases section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Use Cases`; only **Read** the full file if the section cannot be located
2. **Verify** the repository interface exists — run `domain-create-repository` first if missing
3. **Determine** the operation type: GET-single / GET-list / write (POST/PUT) / no-params
4. **Locate** path: `lib/src/features/[feature]/domain/usecases/`
5. **Create** `[verb]_[feature]_usecase.dart`

## UseCase Pattern (GET-single)

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import '../entities/[feature]_entity.dart';
import '../../../../shared/domain/errors/failure.dart';
import '../../../../shared/domain/usecases/use_case.dart';
import '../repositories/[feature]_repository.dart';

@lazySingleton
class Get[Feature]UseCase implements UseCase<[Feature]Entity, String> {
  Get[Feature]UseCase({required this.repository});

  final [Feature]Repository repository;

  @override
  Future<Either<Failure, [Feature]Entity>> call(String id) =>
      repository.get[Feature](id);
}
```

## UseCase Pattern (GET-list with Params)

```dart
@lazySingleton
class Get[Feature]sUseCase
    implements UseCase<List<[Feature]Entity>, Get[Feature]sParams> {
  Get[Feature]sUseCase({required this.repository});

  final [Feature]Repository repository;

  @override
  Future<Either<Failure, List<[Feature]Entity>>> call(
    Get[Feature]sParams params,
  ) =>
      repository.get[Feature]s(page: params.page, limit: params.limit);
}

/// Pure Dart — no freezed, no @JsonKey.
class Get[Feature]sParams {
  const Get[Feature]sParams({this.page = 1, this.limit = 20});
  final int page;
  final int limit;
}
```

## UseCase Pattern (Write)

```dart
@lazySingleton
class Update[Feature]UseCase
    implements UseCase<[Feature]Entity, Update[Feature]Params> {
  Update[Feature]UseCase({required this.repository});

  final [Feature]Repository repository;

  @override
  Future<Either<Failure, [Feature]Entity>> call(
    Update[Feature]Params params,
  ) =>
      repository.update[Feature](params.id, params);
}

/// Pure Dart — no freezed, no @JsonKey.
class Update[Feature]Params {
  const Update[Feature]Params({
    required this.id,
    required this.name,
  });
  final String id;
  final String name;
}
```

## Output

Confirm file paths (UseCase + Params if created) and the method signature.
