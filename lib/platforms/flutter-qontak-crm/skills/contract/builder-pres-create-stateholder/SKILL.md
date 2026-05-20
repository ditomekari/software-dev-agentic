---
name: builder-pres-create-stateholder
description: Create a BLoC with Event and State types for a Flutter Qontak CRM feature. Named constructor params, no @injectable, ViewDataState<T> with .status.isHasData/.status.isError. BLoC is NOT registered in get_it.
user-invocable: false
---

Create a BLoC following `lib/platforms/flutter-qontak-crm/reference/code-architecture/presentation-impl.md ## BLoC`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak-crm/reference/code-architecture/presentation-impl.md` for `## BLoC`; only **Read** the full file if the section cannot be located
2. **Read** the UseCase signatures that this BLoC will call — never guess method names or params
3. **Decide**: BLoC or Cubit? (use Cubit only when there are no events — only direct method calls, no payloads)
4. **Locate** path: `lib/presentation/bloc/[feature]/` (app-level) or `features/[prefix]_[feature]/lib/src/presentation/bloc/[feature]/`
5. **Create** `[feature]_event.dart` → `[feature]_state.dart` → `[feature]_bloc.dart` (as `part of` files)

## BLoC Pattern

```dart
// [feature]_bloc.dart
part '[feature]_event.dart';
part '[feature]_state.dart';

// NOT registered in get_it — BLoC is instantiated inline in route_manager.dart via BlocProvider
class [Feature]Bloc extends Bloc<[Feature]Event, [Feature]State> {
  [Feature]Bloc({
    required this.get[Concept]UseCase,
  }) : super([Feature]State(
         [feature]State: ViewDataState.initial(),
       )) {
    on<Load[Concept]>(_onLoad[Concept]);
  }

  final Get[Concept]UseCase get[Concept]UseCase;

  Future<void> _onLoad[Concept](
    Load[Concept] event,
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
  const factory [Feature]Event.load[Concept]({required String id}) = Load[Concept];
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

## Rules

- Named constructor parameters with `required` — no positional args
- **NOT registered in get_it** — BLoC is instantiated inline in `route_manager.dart` via `BlocProvider`
- Each handler emits `ViewDataState.loading()` first, then folds the result
- `ViewDataState` API: `.status.isHasData`, `.status.isError`, `.status.isLoading`, `.status.isInitial`
- Reset events emit `[Feature]State([feature]State: ViewDataState.noData())`
- BLoC never imports from data layer — no DTOs, no RepositoryImpl, no DataSource
- Add `transformer: sequential()` when BLoC handles loadIndex + loadMore + filter events
- Complex paginated BLoCs may extend `GetIndexBaseBloc` from `crm_core`

## Output

Confirm all file paths created, then **write the stateholder contract file**:

```
.claude/agentic-state/runs/<feature>/stateholder-contract.md
```

Contract format:

```markdown
---
type: bloc | cubit
bloc_class: [Feature]Bloc
state_class: [Feature]State
event_class: [Feature]Event
di: inline
bloc_file: lib/presentation/bloc/[feature]/[feature]_bloc.dart
constructor_params:
  - get[Concept]UseCase: Get[Concept]UseCase
---

## State Fields
| Field | Type | Default |
|---|---|---|
| [feature]State | ViewDataState<[Feature]Entity> | ViewDataState.initial() |

## Events
| Class | Parameters | When to dispatch |
|---|---|---|
| Load[Feature] | id: String | on screen init |
| Reset[Feature] | — | on cleanup / back |

## ViewDataState API (CRM variant)
| Check | UI action |
|---|---|
| .status.isInitial || .status.isLoading | show skeleton |
| .status.isHasData → .data | render content |
| .status.isError → .errorMessage | show error widget |
| .status.isNoData | show empty state |

## Wiring Snippet
\```dart
// Instantiate inline in route_manager.dart or screen entry point — NOT via getIt
BlocProvider<[Feature]Bloc>(
  create: (context) => [Feature]Bloc(
    get[Concept]UseCase: getIt<Get[Concept]UseCase>(),
  )..add(const Load[Feature](id: id)),
  child: BlocBuilder<[Feature]Bloc, [Feature]State>(
    builder: (context, state) {
      final s = state.[feature]State;
      if (s.status.isLoading || s.status.isInitial) return const [Skeleton]();
      if (s.status.isNoData) return const [EmptyWidget]();
      if (s.status.isError) return [ErrorWidget](message: s.errorMessage);
      return [ContentWidget](data: s.data!);
    },
  ),
)
\```
```

Fill every placeholder with the actual values from the files you just created. The wiring snippet must compile — use real class names, not templates.
