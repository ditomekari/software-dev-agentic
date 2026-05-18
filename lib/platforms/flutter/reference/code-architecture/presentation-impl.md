# Flutter — Presentation Layer

> Concepts and invariants: `reference/code-architecture/presentation-theory.md`. This file covers Dart syntax and Flutter-specific patterns.

BLoC pattern for state management. Widgets are dumb — they react to state and dispatch events. Business logic lives in BLoCs via use cases.

---

## State Management <!-- 63 -->

A generic state wrapper for async data operations. Used in every BLoC state that holds fetched or submitted data.

```dart
// presentation/states/view_data_state.dart
import 'package:equatable/equatable.dart';
import '../../domain/errors/failure.dart';

enum ViewState { initial, loading, loaded, error, empty }

class ViewDataState<T> extends Equatable {
  const ViewDataState._({
    required this.status,
    this.data,
    this.message,
    this.failure,
  });

  final ViewState status;
  final T? data;
  final String? message;
  final Failure? failure;

  // Factory constructors
  factory ViewDataState.initial() =>
      const ViewDataState._(status: ViewState.initial);

  factory ViewDataState.loading({String? message}) =>
      ViewDataState._(status: ViewState.loading, message: message);

  factory ViewDataState.loaded({T? data}) =>
      ViewDataState._(status: ViewState.loaded, data: data);

  factory ViewDataState.error({
    required String message,
    Failure? failure,
    T? data,
  }) =>
      ViewDataState._(
        status: ViewState.error,
        message: message,
        failure: failure,
        data: data,
      );

  factory ViewDataState.empty({String? message}) =>
      ViewDataState._(status: ViewState.empty, message: message);

  // Convenience getters
  bool get isInitial => status == ViewState.initial;
  bool get isLoading => status == ViewState.loading;
  bool get isLoaded => status == ViewState.loaded;
  bool get hasError => status == ViewState.error;
  bool get isEmpty => status == ViewState.empty;

  @override
  List<Object?> get props => [status, data, message, failure];
}
```

---

## Events <!-- 37 -->

Sealed classes with freezed. Name with **verb + noun** pattern.

```dart
// presentation/blocs/employee_event.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'employee_event.freezed.dart';

@freezed
sealed class EmployeeEvent with _$EmployeeEvent {
  const factory EmployeeEvent.loadEmployee({
    required String employeeId,
  }) = LoadEmployee;

  const factory EmployeeEvent.refreshEmployee() = RefreshEmployee;

  const factory EmployeeEvent.updateEmployee({
    required String name,
    required String email,
  }) = UpdateEmployee;

  const factory EmployeeEvent.deleteEmployee({
    required String employeeId,
  }) = DeleteEmployee;
}
```

**Event naming:**
- `loadXxx` — initial data fetch
- `refreshXxx` — user-triggered reload
- `submitXxx` / `updateXxx` / `deleteXxx` — mutations
- `selectXxx` / `filterXxx` / `searchXxx` — UI state changes

---

## States <!-- 33 -->

Single immutable state class per BLoC. Use `ViewDataState<T>` for each async operation.

```dart
// presentation/blocs/employee_state.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/employee_entity.dart';
import '../states/view_data_state.dart';

part 'employee_state.freezed.dart';

@freezed
class EmployeeState with _$EmployeeState {
  const factory EmployeeState({
    required ViewDataState<EmployeeEntity> employeeState,
    required ViewDataState<void> updateState,
  }) = _EmployeeState;

  factory EmployeeState.initial() => EmployeeState(
        employeeState: ViewDataState.initial(),
        updateState: ViewDataState.initial(),
      );
}
```

**State rules:**
- One `ViewDataState<T>` per distinct async operation
- `copyWith` for partial updates (provided by freezed)
- No raw booleans like `isLoading` / `hasError` — use `ViewDataState`

---

## BLoC <!-- 88 -->

```dart
// presentation/blocs/employee_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';
import '../../domain/usecases/employee/get_employee_usecase.dart';
import '../../domain/usecases/employee/update_employee_usecase.dart';
import '../states/view_data_state.dart';
import 'employee_event.dart';
import 'employee_state.dart';

@injectable
class EmployeeBloc extends Bloc<EmployeeEvent, EmployeeState> {
  EmployeeBloc({
    required this.getEmployeeUseCase,
    required this.updateEmployeeUseCase,
  }) : super(EmployeeState.initial()) {
    on<LoadEmployee>(_onLoadEmployee);
    on<UpdateEmployee>(_onUpdateEmployee);
  }

  final GetEmployeeUseCase getEmployeeUseCase;
  final UpdateEmployeeUseCase updateEmployeeUseCase;

  Future<void> _onLoadEmployee(
    LoadEmployee event,
    Emitter<EmployeeState> emit,
  ) async {
    emit(state.copyWith(employeeState: ViewDataState.loading()));

    final result = await getEmployeeUseCase(event.employeeId);

    result.fold(
      (failure) => emit(state.copyWith(
        employeeState: ViewDataState.error(
          message: failure.message,
          failure: failure,
        ),
      )),
      (employee) => emit(state.copyWith(
        employeeState: ViewDataState.loaded(data: employee),
      )),
    );
  }

  Future<void> _onUpdateEmployee(
    UpdateEmployee event,
    Emitter<EmployeeState> emit,
  ) async {
    emit(state.copyWith(updateState: ViewDataState.loading()));

    final currentEmployee = state.employeeState.data;
    if (currentEmployee == null) return;

    final params = UpdateEmployeeParams(
      id: currentEmployee.id,
      name: event.name,
      email: event.email,
    );

    final result = await updateEmployeeUseCase(params);

    result.fold(
      (failure) => emit(state.copyWith(
        updateState: ViewDataState.error(
          message: failure.message,
          failure: failure,
        ),
      )),
      (updated) => emit(state.copyWith(
        employeeState: ViewDataState.loaded(data: updated),
        updateState: ViewDataState.loaded(),
      )),
    );
  }
}
```

**BLoC rules:**
- `@injectable` — created fresh per screen via DI
- `on<Event>(_handler)` for each event
- Each handler emits loading first, then result
- Always use `result.fold()` — never `result.getOrElse()` alone
- Use `Emitter<State>` parameter — never call `emit()` directly after `await` in closed blocs

---

## Cubit (Simpler Alternative) <!-- 32 -->

Use Cubit when there are no events — only method calls.

```dart
// presentation/cubits/theme_cubit.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';

@lazySingleton
class ThemeCubit extends Cubit<ThemeMode> {
  ThemeCubit() : super(ThemeMode.light);

  void setLight() => emit(ThemeMode.light);
  void setDark() => emit(ThemeMode.dark);
  void toggle() => emit(
        state == ThemeMode.light ? ThemeMode.dark : ThemeMode.light,
      );
}
```

**BLoC vs Cubit decision:**

| Use BLoC | Use Cubit |
|----------|-----------|
| Complex event-driven flows | Simple state toggles |
| Multiple event handlers | 1-3 method calls |
| Events with payloads | No input needed |
| Needs event replay/transformation | Immediate state updates |

---

## Screen Structure <!-- 59 -->

```dart
// presentation/screens/employee_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../di/injection.dart';
import '../blocs/employee_bloc.dart';
import '../blocs/employee_event.dart';
import '../blocs/employee_state.dart';
import '../widgets/employee_content.dart';

class EmployeeScreen extends StatelessWidget {
  const EmployeeScreen({super.key, required this.employeeId});

  final String employeeId;

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      // getIt creates a fresh BLoC instance
      create: (_) => getIt<EmployeeBloc>()
        ..add(EmployeeEvent.loadEmployee(employeeId: employeeId)),
      child: const _EmployeeView(),
    );
  }
}

class _EmployeeView extends StatelessWidget {
  const _EmployeeView();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Employee')),
      body: BlocBuilder<EmployeeBloc, EmployeeState>(
        buildWhen: (prev, curr) =>
            prev.employeeState != curr.employeeState,
        builder: (context, state) {
          final s = state.employeeState;
          if (s.isLoading || s.isInitial) {
            return const Center(child: CircularProgressIndicator());
          }
          if (s.hasError) {
            return Center(child: Text(s.message ?? 'Error'));
          }
          if (s.data == null) {
            return const Center(child: Text('Not found'));
          }
          return EmployeeContent(employee: s.data!);
        },
      ),
    );
  }
}
```

---

## BlocListener (Side Effects) <!-- 34 -->

Use `BlocListener` for navigation, toasts, dialogs — one-time reactions not reflected in UI.

```dart
BlocListener<EmployeeBloc, EmployeeState>(
  listenWhen: (prev, curr) => prev.updateState != curr.updateState,
  listener: (context, state) {
    if (state.updateState.isLoaded) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Updated successfully')),
      );
      Navigator.of(context).pop();
    }
    if (state.updateState.hasError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.updateState.message ?? 'Failed')),
      );
    }
  },
  child: ...,
)
```

**BlocBuilder vs BlocListener:**

| Use | When |
|-----|------|
| `BlocBuilder` | Rebuild widgets based on state |
| `BlocListener` | Side effects: navigate, show toast, analytics |
| `BlocConsumer` | Both in the same widget tree |

---

## MultiBlocProvider <!-- 22 -->

For screens needing multiple BLoCs:

```dart
MultiBlocProvider(
  providers: [
    BlocProvider(
      create: (_) => getIt<EmployeeBloc>()
        ..add(EmployeeEvent.loadEmployee(employeeId: id)),
    ),
    BlocProvider(
      create: (_) => getIt<AttendanceBloc>()
        ..add(const AttendanceEvent.loadHistory()),
    ),
  ],
  child: const _DashboardView(),
)
```

---

## State Access from Child Widgets <!-- 18 -->

```dart
// In a child widget — read without listening
final bloc = context.read<EmployeeBloc>();
bloc.add(const EmployeeEvent.refreshEmployee());

// Watch — rebuilds on every state change
final state = context.watch<EmployeeBloc>().state;

// Select — rebuilds only when selected value changes
final isLoading = context.select<EmployeeBloc, bool>(
  (bloc) => bloc.state.employeeState.isLoading,
);
```

---

## Shared Component Paths <!-- 11 -->

When running a Component Reuse Check, search these locations for existing reusable widgets:

| Scope | Path | File pattern |
|---|---|---|
| Shared core widgets (cross-feature) | `talenta/lib/src/shared/core/` | `*.dart` |
| Feature screens | `talenta/lib/src/features/*/presentation/screens/` | `*_screen.dart` |
| Feature widgets | `talenta/lib/src/features/*/presentation/widgets/` | `*_widget.dart` |

**Search strategy:** Grep for the widget concept (e.g. `"Card"`, `"Avatar"`, `"EmptyState"`, `"ListItem"`) across `shared/core/` first — widgets there are safe to reuse cross-feature. Only look inside a feature's own `widgets/` folder for local reuse within the same feature. Prefer a `StatelessWidget` found in shared over creating a new one.
