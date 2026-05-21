# Flutter Qontak CRM — Presentation Layer

> Concepts and invariants: `lib/core/reference/code-architecture/presentation-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

BLoC is the sole state management pattern. Widgets are dumb — they react to state and dispatch events. Business logic lives in BLoCs via use cases.

---

## Dependency Rule <!-- 8 -->

Presentation depends on Domain only — no Data layer imports. BLoC and Screen widgets may only import domain use case interfaces, domain entities, and Dart/Flutter primitives.

Forbidden: any `RepositoryImpl`, `DataSourceImpl`, DTO, mapper, `http`/`dio` import, or database type inside the Presentation layer.

---

## ViewDataState (from `qontak_common`) <!-- 26 -->

`ViewDataState<T>` is defined in `qontak_common`. The API surface uses a `.status` field with extension getters — NOT direct bool helpers on `ViewDataState`:

```dart
// Constructors
ViewDataState.initial()                                    // not yet started
ViewDataState.loading()                                    // in flight (optional data retained)
ViewDataState.loaded(data: x)                              // success
ViewDataState.noData()                                     // success, but no content (after reset)
ViewDataState.error(message: m, failure: f)                // error

// Status checks — ALWAYS use .status.* — never use the constructors as booleans
state.companyListState.status.isHasData    // ✅ data available
state.companyListState.status.isLoading    // ✅ loading
state.companyListState.status.isError      // ✅ error
state.companyListState.status.isInitial    // ✅ not yet started

// Access data / failure
state.companyListState.data                // T? — present when isHasData
state.companyListState.failure             // Failure?
state.companyListState.message             // String? error message
```

---

## Events <!-- 21 -->

Events are `@freezed` classes. Named after user intent — verb + noun.

```dart
// features/crm_company/lib/src/presentation/bloc/company/company_event.dart
part of 'company_bloc.dart';

@freezed
class CompanyEvent with _$CompanyEvent {
  const factory CompanyEvent.loadRemoteCompany({@Default(false) bool isRefresh}) = LoadRemoteCompany;
  const factory CompanyEvent.filterCompany({required CompanyFilter filterRequest}) = FilterCompany;
  const factory CompanyEvent.updateIndexAfterCreate() = UpdateIndexAfterCreate;
}
```

- Event variant method names are camelCase: `loadRemoteCompany`, `filterCompany`
- Generated class names (right of `=`) are PascalCase nouns matching the action: `LoadRemoteCompany`, `FilterCompany`

---

## States <!-- 21 -->

```dart
// features/crm_company/lib/src/presentation/bloc/company/company_state.dart
part of 'company_bloc.dart';

@freezed
class CompanyState with _$CompanyState {
  const factory CompanyState({
    required ViewDataState<CompanyList> companyListState,
    required ViewDataState<bool> isMaxReach,
  }) = _CompanyState;
}
```

- All state fields are `ViewDataState<T>` — never raw `isLoading` booleans
- Use `state.copyWith(...)` to emit partial updates
- Initial state: pass `ViewDataState.initial()` to each field in the BLoC `super()` constructor

---

## BLoC <!-- 56 -->

BLoCs use named constructor parameters. No `@injectable` or `@lazySingleton` annotations — registration is manual. BLoCs are **NOT** registered in `get_it` — they are instantiated inline in `route_manager.dart`.

```dart
// features/crm_company/lib/src/presentation/bloc/company/company_bloc.dart
part 'company_event.dart';
part 'company_state.dart';

class CompanyBloc extends Bloc<CompanyEvent, CompanyState> {
  CompanyBloc({
    required this.getCompanyListUseCase,
    required this.filterCompanyUseCase,
  }) : super(CompanyState(
         companyListState: ViewDataState.initial(),
         isMaxReach: ViewDataState.initial(),
       )) {
    on<LoadRemoteCompany>(_onLoadRemoteCompany, transformer: sequential());
    on<FilterCompany>(_onFilterCompany, transformer: sequential());
  }

  final GetCompanyListUseCase getCompanyListUseCase;
  final FilterCompanyUseCase filterCompanyUseCase;

  Future<void> _onLoadRemoteCompany(
    LoadRemoteCompany event,
    Emitter<CompanyState> emit,
  ) async {
    emit(state.copyWith(companyListState: ViewDataState.loading()));

    final result = await getCompanyListUseCase.call(NoParams());

    result.fold(
      (failure) => emit(state.copyWith(
        companyListState: ViewDataState.error(
          message: failure.message,
          failure: failure,
        ),
      )),
      (data) => emit(state.copyWith(
        companyListState: ViewDataState.loaded(data: data),
      )),
    );
  }
}
```

**BLoC rules:**
- Named constructor parameters with `required` — no positional args
- Each handler emits `ViewDataState.loading()` first, then folds the result
- Add `transformer: sequential()` for BLoCs handling `loadIndex` + `loadMore` + `filter` events
- Complex paginated BLoCs may extend `GetIndexBaseBloc` from `crm_core`
- Use `Emitter<State>` — never call `emit()` after `await` on a closed BLoC

---

## Screen Structure <!-- 58 -->

Screens are `StatefulWidget`. Fetch dependencies directly from the accessor in `initState` — not via `context`.

```dart
// features/crm_company/lib/src/presentation/screens/company/company_screen.dart
class CompanyScreen extends StatefulWidget {
  const CompanyScreen({super.key});

  @override
  State<CompanyScreen> createState() => _CompanyScreenState();
}

class _CompanyScreenState extends State<CompanyScreen> {
  late final CompanyBloc _bloc;

  @override
  void initState() {
    super.initState();
    _bloc = qontakCompanyDependency<CompanyBloc>()
      ..add(const CompanyEvent.loadRemoteCompany());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocConsumer<CompanyBloc, CompanyState>(
        bloc: _bloc,
        listenWhen: (prev, curr) =>
            prev.companyListState != curr.companyListState,
        listener: (context, state) {
          if (state.companyListState.status.isError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.companyListState.message ?? 'Failed to load companies'),
              ),
            );
          }
        },
        buildWhen: (prev, curr) =>
            prev.companyListState != curr.companyListState,
        builder: (context, state) {
          if (state.companyListState.status.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.companyListState.data == null) {
            return const Center(child: Text('No companies'));
          }
          return CompanyList(companies: state.companyListState.data!);
        },
      ),
    );
  }
}
```

---

## Route Registration <!-- 21 -->

`BlocProvider` lives in `route_manager.dart`, not inside the screen. The screen only reads state and dispatches events.

```dart
// lib/presentation/route_manager.dart
case AppRoute.company:
  return MaterialPageRoute(
    settings: settings,
    builder: (_) => BlocProvider(
      create: (_) => CompanyBloc(
        getCompanyListUseCase: qontakCompanyDependency(),
        filterCompanyUseCase: qontakCompanyDependency(),
      ),
      child: const CompanyScreen(),
    ),
  );
```

---

## BLoC Count Rules <!-- 18 -->

One BLoC owns one screen's state. A second BLoC is only justified when it satisfies at least one of:

| Condition | Example |
|---|---|
| Independent async lifecycle (separate loading/error state) | `SearchBloc` runs a debounced query while `CompanyBloc` loads the base list |
| Reused across two or more unrelated screens | A global `NotificationBloc` provided at app root |
| Genuinely orthogonal domain operations with separate failure paths | `FormValidationBloc` + `SubmitBloc` |

**Disqualified reasons (do NOT add a BLoC for these):**
- "It felt complex" — split the event enum instead
- Grouping form sub-sections — use nested state fields
- A separate BLoC for a list inside a screen that is not reused elsewhere

---

## BLoC Scope and Reactivity Rules <!-- 20 -->

**Scope rule:** Provide BLoCs at the narrowest widget subtree that needs them. A BLoC provided at route level lives for the duration of that screen. A BLoC provided at app root lives for the entire app session. Never provide a screen-scoped BLoC at app root.

In CRM, BLoCs are instantiated via `MultiBlocProvider` inside `RouteManager`. The provider tree determines scope — add a BLoC inside the route builder for screen-scope, or at the top-level `MultiBlocProvider` in `App` for app-scope.

**Reactivity rule:**
- `context.watch<XxxBloc>()` — re-renders on every state change. Only use if the widget must always reflect the latest state. Never use for a BLoC that changes frequently when the widget only needs infrequent updates.
- `context.read<XxxBloc>()` — does not subscribe. Use for one-time reads and dispatching events. Mandatory inside `BlocListener` callbacks and gesture handlers.
- `BlocSelector` — use to isolate a sub-field so rebuilds only trigger when that field changes.
- `BlocBuilder` with `buildWhen` — use when you need the BLoC's value in the build method but want to gate rebuilds.

---

## Page Initialisation UseCase Pattern <!-- 52 -->

Apply when a screen needs data from more than one repository before it can render. Without this pattern, screens trigger multiple parallel BLoC events on `initState` and merge unrelated loading states in the widget — creating race conditions and redundant error-handling code.

**Diagnostic question:** Does this screen need data from more than one repository?
- No → a single `GetXxxUseCase` called from the BLoC `on<ScreenOpened>` handler is sufficient.
- Yes → introduce a `GetXxxPageDataUseCase` (Page Init UseCase) that returns a `XxxPageData` read model.

**Page Init UseCase:**
```dart
// features/crm_company/lib/src/domain/usecases/get_company_detail_page_data_usecase.dart
class GetCompanyDetailPageDataUseCase
    extends UseCase<CompanyDetailPageData, GetCompanyDetailPageDataParams> {
  final GetCompanyDetailUseCase _getCompany;
  final GetCompanyContactsUseCase _getContacts;

  GetCompanyDetailPageDataUseCase(this._getCompany, this._getContacts);

  @override
  Future<Either<Failure, CompanyDetailPageData>> call(
      GetCompanyDetailPageDataParams params) async {
    final company = await _getCompany(GetCompanyDetailParams(id: params.id));
    return company.flatMap((c) async {
      final contacts = await _getContacts(GetCompanyContactsParams(companyId: c.id));
      return contacts.map((ct) => CompanyDetailPageData(company: c, contacts: ct));
    });
  }
}
```

**BLoC event handler:**
```dart
on<CompanyDetailScreenOpened>((event, emit) async {
  emit(state.copyWith(pageDataState: ViewDataState.loading()));
  final result = await _getPageDataUseCase(
    GetCompanyDetailPageDataParams(id: event.companyId),
  );
  result.fold(
    (failure) => emit(state.copyWith(pageDataState: ViewDataState.error(message: failure.message))),
    (data) => emit(state.copyWith(pageDataState: ViewDataState.hasData(data: data))),
  );
});
```

**DI (CRM manual GetIt):** Register `GetCompanyDetailPageDataUseCase` in `QontakCompanyDependency`:
```dart
getIt.registerLazySingleton<GetCompanyDetailPageDataUseCase>(() =>
  GetCompanyDetailPageDataUseCase(
    getIt<GetCompanyDetailUseCase>(),
    getIt<GetCompanyContactsUseCase>(),
  ),
);
```

---

## BlocListener (Side Effects) <!-- 28 -->
  listener: (context, state) {
    if (state.companyListState.status.isHasData) {
      Navigator.of(context).pop();
    } else if (state.companyListState.status.isError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.companyListState.message ?? 'Error')),
      );
    }
  },
  child: ...,
)
```

| Use | When |
|---|---|
| `BlocBuilder` | Rebuild widgets |
| `BlocListener` | Side effects: navigate, toast, analytics |
| `BlocConsumer` | Both in the same tree |

Key: Use `.status.isHasData` (not `.isLoaded`), `.status.isError` (not `.hasError`).

---

## Shared Component Paths <!-- 9 -->

| Scope | Path |
|---|---|
| Cross-feature widgets | `features/qontak_component_lib/` |
| Feature-local widgets | `features/<pkg>/lib/src/presentation/widgets/` |
| App-shell widgets | `lib/presentation/widgets/` |

Search `qontak_component_lib` first before creating a new component.
