---
name: builder-domain-create-usecase
description: Create a UseCase class for a single business operation in Flutter Qontak. Verb-only name, no UseCase suffix, callable via call().
user-invocable: false
---

Create a UseCase following `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md ## Use Cases section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md` for `## Use Cases`; only **Read** the full file if the section cannot be located
2. **Verify** the repository interface exists — run `builder-domain-create-repository` first if missing
3. **Determine** the operation type: GET-single / GET-list / write (POST/PUT) / no-params
4. **Locate** path: `features/[prefix]_[feature]/lib/src/domain/usecases/`
5. **Create** `[verb]_[concept].dart` — verb-only naming, no `UseCase` suffix

## UseCase Pattern (GET with Params)

```dart
// features/[prefix]_[feature]/lib/src/domain/usecases/get_[concept].dart
import 'package:fpdart/fpdart.dart';
import 'package:[prefix]_core/[prefix]_core.dart'; // re-exports UseCase, NoParams, Failure
import '../entities/[concept].dart';
import '../repositories/[feature]_repository.dart';

class Get[Concept] implements UseCase<[Concept], Get[Concept]Params> {
  Get[Concept]({required this.repository});
  final [Feature]Repository repository;

  @override
  Future<Either<Failure, [Concept]>> call(Get[Concept]Params params) =>
      repository.get[Concept](params.id);
}

class Get[Concept]Params {
  const Get[Concept]Params({required this.id});
  final String id;
}
```

## UseCase Pattern (No Params)

```dart
class GetCurrentUser implements UseCase<User, NoParams> {
  GetCurrentUser({required this.repository});
  final AuthRepository repository;

  @override
  Future<Either<Failure, User>> call(NoParams _) =>
      repository.getCurrentUser();
}
```

## UseCase Pattern (Write)

```dart
class Login implements UseCase<Auth, LoginParams> {
  Login({required this.repository});
  final AuthRepository repository;

  @override
  Future<Either<Failure, Auth>> call(LoginParams params) =>
      repository.login(params.ssoCode);
}

class LoginParams {
  const LoginParams({required this.ssoCode});
  final String ssoCode;
}
```

## Rules

- Verb-only naming, no `UseCase` suffix (`GetInbox`, `Login`, `SendMessage`)
- No `@lazySingleton` — registration is manual in `[Domain]Dependency._registerDomain()`
- Class is callable: `useCase(params)` not `useCase.execute(params)`
- `Params` class: plain Dart, no `@freezed`, no `@JsonKey`
- Never create a use case before the repository abstract class it depends on

## Output

Confirm file paths (UseCase + Params class) and the method signature.
