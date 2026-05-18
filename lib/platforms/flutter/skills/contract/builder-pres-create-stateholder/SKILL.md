---
name: builder-pres-create-stateholder
description: Create a BLoC (or Cubit) with its Event and State types for a feature. Flutter mapping — StateHolder = BLoC.
user-invocable: false
---

> **Flutter mapping**: StateHolder = BLoC (or Cubit for simple state)

Create a BLoC following `.claude/reference/code-architecture/presentation-impl.md ## Events, ## States, ## BLoC sections` and DI rules in `.claude/reference/code-architecture/di-impl.md ## Annotations section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## 2. Events` and `## 3. States`; only **Read** the full file if sections cannot be located
2. **Read** the UseCase signatures that this BLoC will call — never guess method names
3. **Decide**: BLoC or Cubit? (see reference ## Cubit (Simpler Alternative) section — use Cubit for 1-3 simple mutations with no payload)
4. **Locate** path: `lib/src/features/[feature]/presentation/blocs/`
5. **Create** `[feature]_event.dart` → `[feature]_state.dart` → `[feature]_bloc.dart`

## BLoC Pattern

```dart
// [feature]_event.dart
import 'package:freezed_annotation/freezed_annotation.dart';
part '[feature]_event.freezed.dart';

@freezed
sealed class [Feature]Event with _$[Feature]Event {
  const factory [Feature]Event.load[Feature]({required String id}) = Load[Feature];
  const factory [Feature]Event.refresh[Feature]() = Refresh[Feature];
  // verb + noun; see reference ## Events section for naming guide
}

// [feature]_state.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/[feature]_entity.dart';
import '../../../../shared/presentation/states/view_data_state.dart';
part '[feature]_state.freezed.dart';

@freezed
class [Feature]State with _$[Feature]State {
  const factory [Feature]State({
    required ViewDataState<[Feature]Entity> [feature]State,
    // one ViewDataState<T> per distinct async operation
  }) = _[Feature]State;

  factory [Feature]State.initial() => [Feature]State(
        [feature]State: ViewDataState.initial(),
      );
}

// [feature]_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';
import '../../domain/usecases/get_[feature]_usecase.dart';
import '../../../../shared/presentation/states/view_data_state.dart';
import '[feature]_event.dart';
import '[feature]_state.dart';

@injectable
class [Feature]Bloc extends Bloc<[Feature]Event, [Feature]State> {
  [Feature]Bloc({required this.get[Feature]UseCase})
      : super([Feature]State.initial()) {
    on<Load[Feature]>(_onLoad[Feature]);
  }

  final Get[Feature]UseCase get[Feature]UseCase;

  Future<void> _onLoad[Feature](
    Load[Feature] event,
    Emitter<[Feature]State> emit,
  ) async {
    emit(state.copyWith([feature]State: ViewDataState.loading()));
    final result = await get[Feature]UseCase(event.id);
    result.fold(
      (failure) => emit(state.copyWith(
        [feature]State: ViewDataState.error(
          message: failure.message,
          failure: failure,
        ),
      )),
      (entity) => emit(state.copyWith(
        [feature]State: ViewDataState.loaded(data: entity),
      )),
    );
  }
}
```

## Output

Confirm all file paths, list State fields, Event cases, and the use cases injected.
