---
mode: agent
tools:
  - codebase
  - readFile
  - editFiles
  - search
description: "Create a CRM UseCase — <Verb><Entity>UseCase, extends UseCase<T, Params> from qontak_common, returns Future<Either<Failure, T>>. Registers in DI."
---

Create a use case for `$ARGUMENTS`. If not provided, ask: operation (get/create/update/delete), entity name, which repository method it calls.

## Steps

### 1 — Verify repository interface

Search for the `[Feature]Repository` interface in the domain layer. If absent, create the repository interface first before proceeding.

### 2 — Locate path

```
features/[crm_or_qontak]_[feature]/lib/src/domain/usecases/[verb]_[concept]_usecase.dart
```

### 3 — Naming rule

`<Verb><Entity>UseCase` WITH `UseCase` suffix — e.g. `GetCompanyUseCase`, `CreateContactNoteUseCase`, `DeleteTaskUseCase`.

### 4 — Pattern (GET with Params)

```dart
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

### 5 — Pattern (No Params)

```dart
class GetCurrentUserUseCase implements UseCase<User, NoParams> {
  GetCurrentUserUseCase({required this.repository});
  final AuthRepository repository;

  @override
  Future<Either<Failure, User>> call(NoParams _) =>
      repository.getCurrentUser();
}
```

### 6 — Register in DI (CRM manual GetIt)

Add to `Qontak[Feature]Dependency`:

```dart
getIt.registerLazySingleton<Get[Concept]UseCase>(() =>
  Get[Concept]UseCase(repository: getIt<[Feature]Repository>()),
);
```

### Page Init UseCase (multi-repository screens)

If this use case assembles data from 2+ repositories:
- Name it `Get[Screen]PageDataUseCase`
- Return type: `[Screen]PageData` (a `@freezed` read model in `domain/read_models/`)
- Inject the sub-UseCases (not repositories directly) into its constructor
- Register all sub-UseCases in DI first, then register the page-data UseCase last
