# Flutter Qontak — Presentation Layer

> Concepts and invariants: `lib/core/reference/code-architecture/presentation-theory.md`. This file covers Dart syntax and patterns.

BLoC pattern. Widgets are dumb — they react to state and dispatch events. Business logic lives in BLoCs via use cases.

---

## Dependency Rule <!-- 8 -->

Presentation depends on Domain only — no Data layer imports. BLoC and Screen widgets may only import domain use case interfaces, domain entities, and Dart/Flutter primitives.

Forbidden: any `RepositoryImpl`, `DataSourceImpl`, `DTO`, mapper, `http`/`dio` import, or database type inside the Presentation layer.

---

## StateHolder <!-- 12 -->

In Flutter Qontak, the StateHolder is implemented as a **BLoC** (for event-driven flows) or **Cubit** (for simpler state). See `## BLoC` and `## Cubit (Simple State)` below for full implementation patterns.

Invariants:
- Receives use cases via constructor injection — annotated `@injectable`, created fresh per screen via `GetIt.instance`
- Emits immutable `State` objects — never mutates state in place; use `emit(state.copyWith(...))`
- Handles navigation as a side effect via `BlocListener` — not as a direct `Navigator.push` inside the BLoC
- One BLoC/Cubit per screen — scoped to the screen's `BlocProvider`

---

## State <!-- 11 -->

In Flutter Qontak, **State** is an immutable `@freezed` class with a `ViewDataState<T>` field per async operation (from `[prefix]_core`). See `## States` below for the full pattern.

Invariants:
- Immutable — produced by the BLoC via `emit`; widgets observe, never mutate
- One `ViewDataState<T>` per distinct async operation — no raw `isLoading` booleans
- No widget types — no `Color`, `Widget`, `BuildContext` in state classes

---

## Events / Input <!-- 11 -->

In Flutter Qontak (BLoC), Events are `@freezed sealed class` cases dispatched by the widget via `context.read<XBloc>().add(XEvent.loadX())`. In Cubit, they are direct method calls. See `## Events` below.

Invariants:
- Named after user actions using verb + noun — `loadInbox`, `markAsRead`, not `buttonTapped`
- Carry only the data needed — no `BuildContext`, no raw widget references
- Processed by the BLoC's `on<Event>` handler — widgets never act on events directly

---

## Actions / Output <!-- 11 -->

In Flutter Qontak, Actions/Output are navigation and one-time side effects handled via `BlocListener`. See `## BlocListener (Side Effects)` below.

Invariants:
- One-shot — triggered by a state transition (e.g. `markReadState.hasError`), consumed once in `BlocListener`
- Named after the outcome — navigate, show snackbar, close dialog
- Navigation targets are abstract — the BLoC transitions state; the `BlocListener` in the widget decides *how* to navigate

---

## StateHolder Contract <!-- 11 -->

Before `builder-ui-worker` writes the Screen, `builder-feature-worker` produces `.claude/runs/<feature>/stateholder-contract.md` containing:
- BLoC/Cubit class name and file path
- `State` fields (name, type, purpose)
- `Event` cases or Cubit method signatures (name, payload if any)
- Navigation side-effect triggers (which state transition causes navigation)
- DI factory (`@injectable` or `@lazySingleton`)

---

## Creation Order <!-- 10 -->

```
Use Cases → BLoC/Cubit (StateHolder) → StateHolder contract → Screen (builder-ui-worker)
```

Never write the Screen before the StateHolder contract exists.

---

## Layer Invariants <!-- 10 -->

- BLoC/Cubit never imports from the data layer — no DTOs, no `RepositoryImpl`, no `DataSource`
- Use cases injected via constructor — never `GetInbox()` inside a BLoC body
- State is read-only from widgets' perspective — widgets observe via `BlocBuilder`, never mutate
- Navigation side effects are one-shot — triggered via `BlocListener`, not stored in persistent state
- Navigation decisions belong to the widget layer — BLoC transitions state; the listener navigates

---

## ViewDataState (from `qontak_common`) <!-- 34 -->

`ViewDataState<T>` is defined in `qontak_common` (re-exported via `chat_core`). The API surface uses a `.status` field with extension getters — NOT direct bool helpers on `ViewDataState`:

```dart
// Usage pattern (actual codebase)
ViewDataState.initial()         // initial state
ViewDataState.loading()         // loading
ViewDataState.loaded(data: x)   // success with data
ViewDataState.error(message: m, failure: f)  // error
ViewDataState.noData()          // success but no content (e.g. after reset)

// Checking status — use .status extension methods:
state.loginState.status.isHasData   // ✅ data available
state.loginState.status.isError     // ✅ error occurred
state.loginState.status.isLoading   // ✅ loading in progress
state.loginState.status.isInitial   // ✅ not yet started

// Access data/failure
state.loginState.data               // T? — present when isHasData
state.loginState.failure            // Failure? — present when isError
state.loginState.message            // String? — error message
```

**Practical BLoC example from codebase:**

```dart
// lib/presentation/bloc/login/login_bloc.dart
class LoginBloc extends Bloc<LoginEvent, LoginState> {
  LoginBloc({required this.getSSOTokenUseCase, required this.prefHelper})
      : super(LoginState(loginState: ViewDataState.initial())) {
    on<Login>(_onUserLogin);
    on<ResetLogin>(_onResetLogin);
  }

  Future<void> _onUserLogin(Login event, Emitter<LoginState> emit) async {
    emit(state.copyWith(loginState: ViewDataState.loading()));

    final result = await getSSOTokenUseCase.call(
      GetSSOTokenUseCaseParams(ssoCode: event.ssoCode),
    );

    result.fold(
      (failure) => emit(state.copyWith(
        loginState: ViewDataState.error(message: failure.message, failure: failure),
      )),
      (success) {
        prefHelper
          ..setAccessToken(success.accessToken)
          ..setRefreshToken(success.refreshToken);
        emit(state.copyWith(loginState: ViewDataState.loaded(data: success)));
      },
    );
  }

  void _onResetLogin(ResetLogin event, Emitter<LoginState> emit) {
    emit(LoginState(loginState: ViewDataState.noData()));
  }
}
```

---

## Events <!-- 21 -->

Events are `@freezed` classes with named factory constructors. Sealed classes (`sealed class`) are used when the BLoC pattern-matches exhaustively.

```dart
// lib/presentation/bloc/login/login_event.dart
part of 'login_bloc.dart';

@freezed
class LoginEvent with _$LoginEvent {
  const factory LoginEvent.login({required String ssoCode}) = Login;
  const factory LoginEvent.resetLogin() = ResetLogin;
}
```

**Event naming:** `login` / `resetLogin` (verb + noun) · `getFirstRun` / `setFirstRun` (domain verbs) · internal events use `_PrefixedNames` for orchestrator BLoCs.

---

## States <!-- 22 -->

```dart
// lib/presentation/bloc/login/login_state.dart
part of 'login_bloc.dart';

@freezed
class LoginState with _$LoginState {
  const factory LoginState({
    required ViewDataState<Auth> loginState,
  }) = _LoginState;
}
```

One `ViewDataState<T>` per distinct async operation. No raw `isLoading` booleans. Initial state created by passing `ViewDataState.initial()` to the factory constructor.

```dart
// Multi-field state (product_tour_bloc.dart)
@freezed
class ProductTourState with _$ProductTourState {
  const factory ProductTourState({
    required ViewDataState<bool> getFirstRunState,
    required ViewDataState<bool> setFirstRunState,
    required ViewDataState<bool> getQuestStatusState,
    required ViewDataState<bool> setQuestStatusState,
    required ViewDataState<dynamic> getAccountQuestState,
    required ViewDataState<dynamic> setAccountQuestState,
  }) = _ProductTourState;
}
```

---

## BLoC <!-- 42 -->

BLoCs use **named constructor parameters** (not positional). No `@injectable` annotation in the app module — registration is done manually in `MainDependency._registerPresentation()`.

```dart
// lib/presentation/bloc/login/login_bloc.dart
class LoginBloc extends Bloc<LoginEvent, LoginState> {
  LoginBloc({
    required this.getSSOTokenUseCase,
    required this.prefHelper,
  }) : super(LoginState(loginState: ViewDataState.initial())) {
    on<Login>(_onUserLogin);
    on<ResetLogin>(_onResetLogin);
  }

  final ChatPrefHelper prefHelper;
  final GetSSOTokenUseCase getSSOTokenUseCase;

  Future<void> _onUserLogin(Login event, Emitter<LoginState> emit) async {
    emit(state.copyWith(loginState: ViewDataState.loading()));

    final result = await getSSOTokenUseCase.call(
      GetSSOTokenUseCaseParams(ssoCode: event.ssoCode),
    );

    result.fold(
      (failure) => emit(state.copyWith(
        loginState: ViewDataState.error(message: failure.message, failure: failure),
      )),
      (success) {
        prefHelper
          ..setAccessToken(success.accessToken)
          ..setRefreshToken(success.refreshToken);
        emit(state.copyWith(loginState: ViewDataState.loaded(data: success)));
      },
    );
  }

  void _onResetLogin(ResetLogin event, Emitter<LoginState> emit) {
    emit(LoginState(loginState: ViewDataState.noData()));
  }
}
```

**BLoC rules:**
- Named constructor parameters with `required` — no positional args
- No `@injectable` in the app module — use `registerFactory` in `MainDependency`
- Each handler emits loading first, then result via `result.fold()`
- Use `Emitter<State>` — never call `emit()` after `await` on a closed BLoC

---

## Screen Structure <!-- 38 -->

Screens do NOT own `BlocProvider` — that lives in `route_manager.dart`. The screen just reads state and dispatches events.

```dart
// lib/presentation/screens/login/login_screen.dart
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocConsumer<LoginBloc, LoginState>(
        listenWhen: (prev, curr) => prev.loginState != curr.loginState,
        listener: (context, state) {
          if (state.loginState.status.isHasData) {
            Navigator.of(context).pushReplacementNamed(QontakAppRoute.main);
          } else if (state.loginState.status.isError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.loginState.message ?? 'Login failed')),
            );
          }
        },
        buildWhen: (prev, curr) => prev.loginState != curr.loginState,
        builder: (context, state) {
          if (state.loginState.status.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return LoginForm(
            onLogin: (ssoCode) =>
                context.read<LoginBloc>().add(LoginEvent.login(ssoCode: ssoCode)),
          );
        },
      ),
    );
  }
}
```

The `BlocProvider` is in `route_manager.dart`:
```dart
case QontakAppRoute.login:
  return BlocProvider(
    create: (_) => LoginBloc(
      getSSOTokenUseCase: mainDependency(),
      prefHelper: coreDependency(),
    ),
    child: const LoginScreen(),
  );
```

---

## BlocListener (Side Effects) <!-- 24 -->

```dart
BlocListener<ResolveRoomBloc, ResolveRoomState>(
  listenWhen: (prev, curr) => prev.resolveState != curr.resolveState,
  listener: (context, state) {
    if (state.resolveState.status.isHasData) {
      Navigator.of(context).pop();
    } else if (state.resolveState.status.isError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.resolveState.message ?? 'Failed')),
      );
    }
  },
  child: ...,
)
```

**Key:** Use `.status.isHasData` and `.status.isError` (not `.isLoaded` / `.hasError`) — those are extension methods on the `ViewDataStatus` enum from `qontak_common`.

| Use | When |
|---|---|
| `BlocBuilder` | Rebuild widgets |
| `BlocListener` | Side effects: navigate, toast, analytics |
| `BlocConsumer` | Both in the same tree |

---

## Cubit (Simple State) <!-- 14 -->

```dart
@lazySingleton
class ThemeCubit extends Cubit<ThemeMode> {
  ThemeCubit() : super(ThemeMode.light);
  void toggle() => emit(state == ThemeMode.light ? ThemeMode.dark : ThemeMode.light);
}
```

Use Cubit when there are no events — only direct method calls, no payloads.

---

## Shared Component Paths <!-- 8 -->

| Scope | Path |
|---|---|
| Cross-feature widgets | `shared/[prefix]_core/lib/src/widgets/` |
| Feature-local widgets | `features/[prefix]_xxx/lib/src/presentation/widgets/` |

Search `[prefix]_core` widgets first before creating a new one.
