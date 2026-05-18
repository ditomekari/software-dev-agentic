---
name: flutter-qontak-crm-add-usecase
description: Add a domain use case to a Qontak CRM feature package, wire it to its repository, and register it in DI.
user-invocable: false
---

## Steps

### 1 — Determine the use case's place in the domain

Use cases live in `features/crm_<domain>/lib/src/domain/usecases/`.

Naming convention: `<Verb><Entity>UseCase`

| Verb | When to use |
|---|---|
| `Get` | Read a single entity |
| `GetList` / `Search` | Read a collection |
| `Add` | Create |
| `Edit` / `Update` | Modify |
| `Delete` | Remove |
| `Sync` | Sync local ↔ remote |
| `Filter` | Filtered fetch |

### 2 — Write the use case class

`features/crm_<domain>/lib/src/domain/usecases/<verb>_<entity>_usecase.dart`:

**Simple use case (single param):**
```dart
import 'package:crm_core/crm_dependency.dart' hide Failure;
import 'package:crm_core/qontak_common.dart';
import 'package:crm_<domain>/src/domain/domains.dart';

class Get<Entity>ByIdUseCase extends UseCase<<Entity>, String> {
  Get<Entity>ByIdUseCase({required this.repository});
  final <Entity>Repository repository;

  @override
  Future<Either<Failure, <Entity>>> call(String params) =>
      repository.get<Entity>ById(id: params);
}
```

**Use case with a dedicated params entity:**
```dart
import 'package:crm_core/crm_dependency.dart' hide Failure;
import 'package:crm_core/qontak_common.dart';
import 'package:crm_<domain>/src/domain/domains.dart';

class Get<Entity>FilteredListUseCase extends UseCase<<Entity>List, <Entity>Filter> {
  Get<Entity>FilteredListUseCase({required this.repository});
  final <Entity>Repository repository;

  @override
  Future<Either<Failure, <Entity>List>> call(<Entity>Filter params) =>
      repository.filter<Entity>(filterRequest: params);
}
```

**No-params use case** (use `NoParams` from `qontak_common`):
```dart
class GetAll<Entity>LocalUseCase extends UseCase<List<<Entity>>, NoParams> {
  GetAll<Entity>LocalUseCase({required this.repository});
  final <Entity>Repository repository;

  @override
  Future<Either<Failure, List<<Entity>>>> call(NoParams params) =>
      repository.getAll<Entity>sLocal();
}
```

Rules:
- Use cases contain no business logic beyond delegation. They call exactly one repository method.
- The type params of `UseCase<ReturnType, Params>` must match exactly what the BLoC passes to `.call(...)`.
- Never import data-layer types in a use case. Only domain entities.

### 3 — (If needed) Create a params entity

If the use case needs a structured params object, create a `@freezed` entity:

`features/crm_<domain>/lib/src/domain/entities/<entity>_params/<entity>_params.dart`:
```dart
import 'package:crm_core/crm_dependency.dart';

part '<entity>_params.freezed.dart';

@freezed
class <Entity>Params with _$<Entity>Params {
  const factory <Entity>Params({
    String? id,
    int? page,
    // ... other filter/query fields
  }) = _<Entity>Params;
}
```

Run `build_runner` to generate `.freezed.dart`.

### 4 — Add to the domain barrel

In `lib/src/domain/domain.dart` (or `usecases/usecases.dart`), add:
```dart
export 'usecases/<verb>_<entity>_usecase.dart';
```

### 5 — Register in DI

In `lib/src/config/di/qontak_<domain>_dependency.dart`, in `_register<Domain>Domain()`:

```dart
qontak<Domain>Dependency.registerLazySingleton<Get<Entity>ByIdUseCase>(
  () => Get<Entity>ByIdUseCase(repository: qontak<Domain>Dependency()),
);
```

Registration order: all data-layer registrations (data sources, repositories) must come before domain registrations in the same `register<Domain>()` call.

### 6 — Inject into a BLoC

In the BLoC constructor:
```dart
class <Name>Bloc extends Bloc<<Name>Event, <Name>State> {
  <Name>Bloc({
    required this.get<Entity>ByIdUseCase,
  }) : super(...) {
    on<Get<Entity>ById>(_onGet<Entity>ById);
  }

  final Get<Entity>ByIdUseCase get<Entity>ByIdUseCase;

  Future<void> _onGet<Entity>ById(
    Get<Entity>ById event,
    Emitter<<Name>State> emit,
  ) async {
    emit(state.copyWith(<entity>State: ViewDataState.loading()));
    final result = await get<Entity>ByIdUseCase.call(event.id);
    result.fold(
      (failure) => emit(state.copyWith(
        <entity>State: ViewDataState.error(message: failure.message, failure: failure),
      )),
      (data) => emit(state.copyWith(
        <entity>State: ViewDataState.loaded(data: data),
      )),
    );
  }
}
```

Instantiate the BLoC at the usage site (route or BlocProvider), passing the use case from the DI accessor:
```dart
BlocProvider<<Name>Bloc>(
  create: (_) => <Name>Bloc(
    get<Entity>ByIdUseCase: qontak<Domain>Dependency(),
  ),
  child: const <Screen>(),
)
```

### 7 — Run code generation (if params entity was created)

```bash
cd features/crm_<domain>
dart run build_runner build --delete-conflicting-outputs
```
