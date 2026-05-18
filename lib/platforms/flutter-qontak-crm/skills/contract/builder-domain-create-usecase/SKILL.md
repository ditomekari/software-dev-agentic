---
name: builder-domain-create-usecase
description: Create a UseCase class for a single business operation in Flutter Qontak CRM. Named <Verb><Entity>UseCase, extends UseCase<T, Params> from qontak_common.
user-invocable: false
---

Create a UseCase following `lib/platforms/flutter-qontak-crm/reference/code-architecture/domain-impl.md ## Use Cases`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak-crm/reference/code-architecture/domain-impl.md` for `## Use Cases`; only **Read** the full file if the section cannot be located
2. **Verify** the repository interface exists — run `builder-domain-create-repository` first if missing
3. **Determine** the operation type: GET-single / GET-list / write (POST/PUT) / no-params
4. **Locate** path: `features/[prefix]_[feature]/lib/src/domain/usecases/`
5. **Create** `[verb]_[concept]_usecase.dart` — naming: `<Verb><Entity>UseCase` WITH `UseCase` suffix

## UseCase Pattern (GET with Params)

```dart
// features/[prefix]_[feature]/lib/src/domain/usecases/get_[concept]_usecase.dart
import 'package:fpdart/fpdart.dart';
import 'package:qontak_common/qontak_common.dart'; // re-exports UseCase, NoParams, Failure
import '../entities/[concept].dart';
import '../repositories/[feature]_repository.dart';

class Get[Concept]UseCase implements UseCase<[Concept], Get[Concept]Params> {
  Get[Concept]UseCase({required this.repository});
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
class GetCurrentUserUseCase implements UseCase<AuthToken, NoParams> {
  GetCurrentUserUseCase({required this.repository});
  final AuthRepository repository;

  @override
  Future<Either<Failure, AuthToken>> call(NoParams _) =>
      repository.getCurrentUser();
}
```

## UseCase Pattern (Write)

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

## Rules

- Naming: `<Verb><Entity>UseCase` WITH `UseCase` suffix — e.g. `GetCompanyUseCase`, `AddCompanyUseCase`
- No `@lazySingleton` — registration is manual in `Qontak[Feature]Dependency._register[Feature]Domain()`
- Class is callable: `useCase(params)` not `useCase.execute(params)`
- `Params` class: plain Dart, no `@freezed`, no `@JsonKey`
- Never create a use case before the repository abstract class it depends on

## Output

Confirm file paths (UseCase + Params class) and the method signature.
