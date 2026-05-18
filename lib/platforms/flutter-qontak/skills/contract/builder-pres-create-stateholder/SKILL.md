---
name: builder-pres-create-stateholder
description: Create a BLoC (or Cubit) with Event and State types for a Flutter Qontak feature. Named constructor params, no @injectable, ViewDataState<T> API with .status.isHasData/.status.isError.
user-invocable: false
---

Create a BLoC following `lib/platforms/flutter-qontak/reference/code-architecture/presentation-impl.md ## BLoC`, `## Events`, and `## States sections`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/presentation-impl.md` for `## BLoC` and `## Events`; only **Read** the full file if sections cannot be located
2. **Read** the UseCase signatures that this BLoC will call — never guess method names or params
3. **Decide**: BLoC or Cubit? (use Cubit only when there are no events — only direct method calls, no payloads)
4. **Locate** path: `lib/presentation/bloc/[feature]/` (app-level) or `features/[prefix]_[feature]/lib/src/presentation/blocs/`
5. **Create** `[feature]_event.dart` → `[feature]_state.dart` → `[feature]_bloc.dart` (as `part of` files)

## BLoC Pattern

```dart
// [feature]_bloc.dart
part '[feature]_event.dart';
part '[feature]_state.dart';

// No @injectable — BLoC is registered via registerFactory in [Domain]Dependency._registerPresentation()
class [Feature]Bloc extends Bloc<[Feature]Event, [Feature]State> {
  [Feature]Bloc({
    required this.get[Concept]UseCase,
  }) : super([Feature]State(
         [feature]State: ViewDataState.initial(),
       )) {
    on<[EventCase]>(_on[EventCase]);
  }

  final Get[Concept] get[Concept]UseCase; // verb-only use case name

  Future<void> _on[EventCase](
    [EventCase] event,
    Emitter<[Feature]State> emit,
  ) async {
    emit(state.copyWith([feature]State: ViewDataState.loading()));

    final result = await get[Concept]UseCase.call(
      Get[Concept]Params(id: event.id),
    );

    result.fold(
      (failure) => emit(state.copyWith(
        [feature]State: ViewDataState.error(
          message: failure.message,
          failure: failure,
        ),
      )),
      (data) => emit(state.copyWith(
        [feature]State: ViewDataState.loaded(data: data),
      )),
    );
  }
}
```

```dart
// [feature]_event.dart
part of '[feature]_bloc.dart';

@freezed
class [Feature]Event with _$[Feature]Event {
  const factory [Feature]Event.[verb][Concept]({required String id}) = [Verb][Concept];
  const factory [Feature]Event.reset[Feature]() = Reset[Feature];
}
```

```dart
// [feature]_state.dart
part of '[feature]_bloc.dart';

@freezed
class [Feature]State with _$[Feature]State {
  const factory [Feature]State({
    required ViewDataState<[Concept]> [feature]State,
    // one ViewDataState<T> per distinct async operation — no raw isLoading booleans
  }) = _[Feature]State;
}
```

## DI Registration (caller adds to [Domain]Dependency)

```dart
// In [Domain]Dependency._registerPresentation():
[domain]Dependency.registerFactory(() => [Feature]Bloc(
  get[Concept]UseCase: [domain]Dependency(),
));
```

## Rules

- Named constructor parameters with `required` — no positional args
- No `@injectable` — registration is manual via `registerFactory`
- Each handler emits `ViewDataState.loading()` first, then folds the result
- `ViewDataState` API: `.status.isHasData`, `.status.isError`, `.status.isLoading`, `.status.isInitial`
- Reset events emit `[Feature]State([feature]State: ViewDataState.noData())`
- BLoC never imports from data layer — no DTOs, no RepositoryImpl, no DataSource

## Output

Confirm all file paths, list State fields with types, Event cases, and use cases injected.
