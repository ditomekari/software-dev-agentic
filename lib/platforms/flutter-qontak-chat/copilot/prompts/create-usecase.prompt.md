---
mode: agent
tools:
  - codebase
  - readFile
  - editFiles
  - search
description: "Create a Chat UseCase — <Verb><Entity>UseCase, @lazySingleton, returns Future<Either<Failure, T>>. Auto-wired by @injectable codegen."
---

Create a use case for `$ARGUMENTS`. If not provided, ask: operation (get/create/update/delete), entity name, which repository method it calls.

## Steps

### 1 — Verify repository interface

Search for the `[Feature]Repository` interface in the domain layer. If absent, create the repository interface first before proceeding.

### 2 — Locate path

```
features/[prefix]_[feature]/lib/src/domain/usecases/[verb]_[concept]_usecase.dart
```

### 3 — Naming rule

`<Verb><Entity>UseCase` WITH `UseCase` suffix — e.g. `GetRoomUseCase`, `SendMessageUseCase`, `ResolveRoomUseCase`.

### 4 — Pattern (GET with Params)

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:[prefix]_core/[prefix]_core.dart'; // re-exports UseCase, NoParams, Failure
import '../entities/[concept].dart';
import '../repositories/[feature]_repository.dart';

@lazySingleton
class Get[Concept]UseCase implements UseCase<[Concept], Get[Concept]Params> {
  Get[Concept]UseCase(this._repository);
  final [Feature]Repository _repository;

  @override
  Future<Either<Failure, [Concept]>> call(Get[Concept]Params params) =>
      _repository.get[Concept](params.id);
}

class Get[Concept]Params {
  const Get[Concept]Params({required this.id});
  final String id;
}
```

### 5 — Pattern (No Params)

```dart
@lazySingleton
class GetCurrentSessionUseCase implements UseCase<Session, NoParams> {
  GetCurrentSessionUseCase(this._repository);
  final SessionRepository _repository;

  @override
  Future<Either<Failure, Session>> call(NoParams _) =>
      _repository.getCurrentSession();
}
```

### 6 — DI (Chat @injectable)

Adding `@lazySingleton` is sufficient — the `@injectable` codegen wires the constructor automatically. Run `flutter pub run build_runner build` after creating the file to regenerate `injection.config.dart`.

Do NOT manually add registration in `MainDependency` — that is only for BLoCs.

### Page Init UseCase (multi-repository screens)

If this use case assembles data from 2+ repositories:
- Name it `Get[Screen]PageDataUseCase`
- Return type: `[Screen]PageData` (a `@freezed` read model in `domain/read_models/`)
- Annotate with `@lazySingleton` — codegen auto-wires sub-UseCase constructor dependencies
- No manual DI registration needed
