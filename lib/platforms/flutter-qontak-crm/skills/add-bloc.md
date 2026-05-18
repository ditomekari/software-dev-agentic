---
name: flutter-qontak-crm-add-bloc
description: Add a BLoC (event, state, bloc) for a use case inside a Qontak CRM feature package, following the freezed union pattern.
user-invocable: false
---

## Steps

### 1 — Determine placement

- **Feature BLoC**: `features/crm_<domain>/lib/src/presentation/bloc/<feature_name>/`
- **App-shell BLoC** (auth, bottom nav, etc.): `lib/presentation/bloc/<feature_name>/`

Create the folder. It will contain four files:
- `<name>_bloc.dart`
- `<name>_event.dart`
- `<name>_state.dart`
- `<name>_bloc.freezed.dart` (generated — do not write manually)

### 2 — Write the event file

`<name>_event.dart`:
```dart
part of '<name>_bloc.dart';

@freezed
class <Name>Event with _$<Name>Event {
  const factory <Name>Event.<verb>({
    required String param,
  }) = <VerbEntity>;

  // Add more variants as needed:
  const factory <Name>Event.reset() = Reset<Name>;
}
```

Rules:
- Event variants are named after user/system intent in camelCase on the left: `<Name>Event.loadData(...)`.
- The generated class name (right of `=`) is PascalCase describing the action: `LoadData`, `Reset<Name>`.
- Use `@Default(value)` for optional params with defaults.

### 3 — Write the state file

`<name>_state.dart`:
```dart
part of '<name>_bloc.dart';

@freezed
class <Name>State with _$<Name>State {
  const factory <Name>State({
    required ViewDataState<<Entity>> <entity>State,
    // Add more ViewDataState fields per concern:
    // required ViewDataState<bool> isSubmitting,
  }) = _<Name>State;
}
```

Rules:
- Every state field must be `ViewDataState<T>` from `qontak_common`.
- Initialize with `ViewDataState.initial()` in the BLoC's `super(...)` call.
- Never use raw booleans or nullable types for async status — use `ViewDataState<bool>`.

### 4 — Write the BLoC file

`<name>_bloc.dart`:
```dart
import 'package:crm_core/crm_dependency.dart';
import 'package:crm_core/qontak_common.dart';
import 'package:crm_<domain>/src/domain/usecases/<verb>_<entity>_usecase.dart';
import 'package:crm_<domain>/src/domain/entities/<entity>/<entity>.dart';

part '<name>_bloc.freezed.dart';
part '<name>_event.dart';
part '<name>_state.dart';

class <Name>Bloc extends Bloc<<Name>Event, <Name>State> {
  <Name>Bloc({
    required this.<verb><Entity>UseCase,
  }) : super(
          <Name>State(
            <entity>State: ViewDataState.initial(),
          ),
        ) {
    on<<Verb><Entity>>(_on<Verb><Entity>);
  }

  final <Verb><Entity>UseCase <verb><Entity>UseCase;

  Future<void> _on<Verb><Entity>(
    <Verb><Entity> event,
    Emitter<<Name>State> emit,
  ) async {
    emit(state.copyWith(<entity>State: ViewDataState.loading()));

    final result = await <verb><Entity>UseCase.call(event.param);

    result.fold(
      (failure) => emit(
        state.copyWith(
          <entity>State: ViewDataState.error(
            message: failure.message,
            failure: failure,
          ),
        ),
      ),
      (data) => emit(
        state.copyWith(
          <entity>State: ViewDataState.loaded(data: data),
        ),
      ),
    );
  }
}
```

Rules:
- Inject all use cases via named constructor parameters. No `get_it` calls inside the BLoC.
- For list BLoCs with sequential load/load-more/filter events, add `transformer: sequential()` to the `on<Event>()` registration.
- For paginated lists, consider extending `GetIndexBaseBloc` from `crm_core`.

### 5 — Add to the presentation barrel

In `lib/src/presentation/presentation.dart` (or `bloc/bloc.dart`), add an export:
```dart
export 'bloc/<name>/<name>_bloc.dart';
```

### 6 — Register the BLoC at usage site

BLoCs are NOT registered in `get_it`. Instantiate them in the route or screen:
```dart
BlocProvider<<Name>Bloc>(
  create: (_) => <Name>Bloc(
    <verb><Entity>UseCase: qontak<Domain>Dependency(),
  ),
  child: const <Screen>(),
)
```

Or in `MultiBlocProvider` if multiple BLoCs are needed for a route.

### 7 — Run code generation

```bash
cd features/crm_<domain>
dart run build_runner build --delete-conflicting-outputs
```

Verify `<name>_bloc.freezed.dart` is generated with no errors.

### 8 — Consume in the screen

Use `BlocConsumer` (listener + builder) or `BlocBuilder` (builder only):

```dart
BlocConsumer<<Name>Bloc, <Name>State>(
  listener: (context, state) {
    if (state.<entity>State.status.isHasData) {
      // navigate or show success
    }
    if (state.<entity>State.status.isError) {
      MpToast.error(state.<entity>State.failure?.message ?? '').show(context);
    }
  },
  builder: (context, state) {
    if (state.<entity>State.status.isLoading) return const CircularProgressIndicator();
    if (state.<entity>State.status.isHasData) return <DataWidget>(data: state.<entity>State.data!);
    return const SizedBox.shrink();
  },
)
```

Trigger events with:
```dart
context.read<<Name>Bloc>().add(const <Name>Event.<verb>());
```
