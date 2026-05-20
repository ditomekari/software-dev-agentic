---
name: builder-pres-create-stateholder
description: Create a BLoC with its Event and State types for a feature. Flutter mapping — StateHolder = BLoC.
user-invocable: false
---

> **Flutter mapping**: StateHolder = BLoC (or Cubit for 1-3 simple mutations with no payload)

Create a BLoC following `.claude/reference/code-architecture/presentation-impl.md ## State section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## State`; only **Read** the full file if the section cannot be located
2. **Read** the UseCase signatures that this BLoC will call — never guess method names
3. **Decide**: BLoC (events with payload, pagination, complex flows) or Cubit (simple toggle/flag mutations)
4. **Locate** path: `features/<feature>/lib/src/presentation/blocs/<feature_name>/`
5. **Create** `<feature>_event.dart` → `<feature>_state.dart` → `<feature>_bloc.dart`

## BLoC Pattern

```dart
// <feature>_bloc.dart
import 'package:jurnal_core/jurnal_core.dart';

part '<feature>_bloc.freezed.dart';
part '<feature>_event.dart';
part '<feature>_state.dart';

class <Feature>Bloc extends Bloc<<Feature>Event, <Feature>State> {
  <Feature>Bloc(this.useCase)
      : super(const <Feature>State(state: ViewDataInitial())) {
    on<Get<Feature>s>(_onLoad);
    on<GetMore<Feature>s>(_onLoadMore);
  }

  final Get<Feature>ListUseCase useCase;
  static const int _pageSize = 20;

  Future<void> _onLoad(Get<Feature>s event, Emitter<<Feature>State> emit) async {
    if (state.state is ViewDataLoading) return;
    emit(state.copyWith(state: const ViewDataLoading(), page: 1));

    final result = await useCase.call(Get<Feature>ListParams(
      page: 1,
      pageSize: _pageSize,
      searchKey: event.searchKey,
    ));

    result.when(
      success: (data) {
        if (data == null || data.items.isEmpty) {
          emit(state.copyWith(state: const ViewDataEmpty()));
        } else {
          emit(state.copyWith(
            state: ViewDataState.success(data),
            hasMore: data.items.length >= _pageSize,
          ));
        }
      },
      failure: (f) => emit(state.copyWith(state: ViewDataFailure(f.toFailure()))),
    );
  }
}

// <feature>_event.dart
@freezed
class <Feature>Event with _$<Feature>Event {
  const factory <Feature>Event.get<Feature>s({
    String? searchKey,
    @Default(false) bool fullRefresh,
  }) = Get<Feature>s;
  const factory <Feature>Event.getMore<Feature>s() = GetMore<Feature>s;
}

// <feature>_state.dart
@freezed
class <Feature>State with _$<Feature>State {
  const factory <Feature>State({
    required ViewDataState<<Entity>> state,
    @Default(1) int page,
    @Default(false) bool hasMore,
    String? searchKey,
  }) = _<Feature>State;
}
```

## Output

Confirm all file paths created, then **write the stateholder contract file**:

```
.claude/agentic-state/runs/<feature>/stateholder-contract.md
```

Contract format:

```markdown
---
type: bloc | cubit
bloc_class: <Feature>Bloc
state_class: <Feature>State
event_class: <Feature>Event
import_bloc: package:jurnal_<module>/src/presentation/blocs/<feature>/<feature>_bloc.dart
import_state: package:jurnal_<module>/src/presentation/blocs/<feature>/<feature>_state.dart
import_event: package:jurnal_<module>/src/presentation/blocs/<feature>/<feature>_event.dart
---

## State Fields
| Field | Type | Default |
|---|---|---|
| <field> | ViewDataState<<Entity>> | ViewDataInitial() |

## Events
| Class | Factory | Parameters | When to dispatch |
|---|---|---|---|
| Get<Feature>s | <Feature>Event.get<Feature>s | searchKey: String? | on screen init / search |

## ViewDataState Variants
| Variant | UI action |
|---|---|
| ViewDataInitial | show skeleton |
| ViewDataLoading | show skeleton |
| ViewDataState\<T\> (success) | render content |
| ViewDataEmpty | show empty state |
| ViewDataFailure | show error widget |

## Wiring Snippet
\```dart
BlocProvider<[BlocClass]>(
  create: (context) => getIt<[BlocClass]>()..add(const [InitialEvent]()),
  child: BlocBuilder<[BlocClass], [StateClass]>(
    builder: (context, state) {
      final s = state.[stateField];
      if (s is ViewDataLoading || s is ViewDataInitial) return const [Skeleton]();
      if (s is ViewDataEmpty) return const [EmptyWidget]();
      if (s is ViewDataFailure) return [ErrorWidget](failure: s.failure);
      final data = (s as ViewDataState<[Entity]>).data!;
      return [ContentWidget](data: data);
    },
  ),
)
\```
```

Fill every placeholder with the actual values from the files you just created. The wiring snippet must compile — use real class names, not templates.
