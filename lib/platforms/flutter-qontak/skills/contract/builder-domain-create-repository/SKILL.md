---
name: builder-domain-create-repository
description: Create a Domain Repository abstract class for a Flutter Qontak feature. Returns Either<Failure, T>, never throws.
user-invocable: false
---

Create a Repository interface following `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md ## Repository Interfaces section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md` for `## Repository Interfaces`; only **Read** the full file if the section cannot be located
2. **Verify** the entity exists in `features/[prefix]_[feature]/lib/src/domain/entities/`
3. **Locate** path: `features/[prefix]_[feature]/lib/src/domain/repositories/`
4. **Create** `[feature]_repository.dart`

## Repository Pattern

```dart
// features/[prefix]_[feature]/lib/src/domain/repositories/[feature]_repository.dart
import 'package:fpdart/fpdart.dart';
import 'package:[prefix]_core/[prefix]_core.dart'; // re-exports Failure
import '../entities/[concept].dart';

abstract class [Feature]Repository {
  // all methods return Either<Failure, T> — never throw
  Future<Either<Failure, [Concept]>> get[Concept](String id);
  Future<Either<Failure, List<[Concept]>>> get[Concept]s();
  Future<Either<Failure, [Concept]>> update[Concept](String id, Update[Concept]Params params);
  Future<Either<Failure, void>> delete[Concept](String id);
}
```

## Rules

- `abstract class` — never `interface` or `mixin`
- Return `Either<Failure, T>` — never throw
- Return domain entities (e.g. `[Concept]`), not DTOs (`[Concept]Response`)
- Repository interface belongs in domain; implementation belongs in data
- Import from `package:[prefix]_core` for `Failure` — never from data or presentation
- Use `package:` imports, never relative paths across package boundaries

## Output

Confirm file path and list all declared method signatures.
