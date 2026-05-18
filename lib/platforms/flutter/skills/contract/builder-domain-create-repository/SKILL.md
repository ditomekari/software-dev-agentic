---
name: builder-domain-create-repository
description: Create a Domain Repository abstract class for a new feature.
user-invocable: false
---

Create a Repository interface following `.claude/reference/code-architecture/domain-impl.md ## Repository Interfaces section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Repository Interfaces`; only **Read** the full file if the section cannot be located
2. **Verify** the entity exists in `lib/src/features/[feature]/domain/entities/`
3. **Locate** path: `lib/src/features/[feature]/domain/repositories/`
4. **Create** `[feature]_repository.dart`

## Repository Pattern

```dart
import 'package:fpdart/fpdart.dart';
import '../entities/[feature]_entity.dart';
import '../../../../shared/domain/errors/failure.dart';

abstract class [Feature]Repository { // abstract class — never interface or mixin
  // all methods return Either<Failure, T> — never throw; params use Params objects not Map
  Future<Either<Failure, [Feature]Entity>> get[Feature](String id);
  Future<Either<Failure, List<[Feature]Entity>>> get[Feature]s({
    int page = 1,
    int limit = 20,
  });
  Future<Either<Failure, [Feature]Entity>> update[Feature](
    String id,
    Update[Feature]Params params,
  );
  Future<Either<Failure, void>> delete[Feature](String id);
}
```

## Output

Confirm file path and list all declared method signatures.
