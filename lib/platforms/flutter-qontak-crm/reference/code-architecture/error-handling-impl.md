# Flutter Qontak CRM — Error Handling

> Concepts and invariants: `lib/core/reference/code-architecture/error-handling-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

Errors flow from DataSource (throws exception) → RepositoryImpl (catches, returns `Left<Failure>`) → BLoC (emits `ViewDataState.error`) → Screen (`BlocListener`).

---

## Error Flow <!-- 10 -->

```
DataSource        throws Exception
      ↓
RepositoryImpl    catches → returns Left(Failure(...))
      ↓
UseCase           passes Left through — no catch
      ↓
BLoC              result.fold → emits ViewDataState.error(message:, failure:)
      ↓
Screen            BlocListener: state.*.status.isError → show SnackBar / dialog
```

---

## Failure (from `qontak_common`) <!-- 12 -->

`Failure` is defined in `qontak_common` and used across all layers.

```dart
// Usage in repository — return Left(Failure(...)) on error
Left(Failure(message: 'Could not load companies'))

// Usage in BLoC — access from state
state.companyListState.failure        // Failure?
state.companyListState.message        // String?
```

---

## Repository Error Handling <!-- 20 -->

Two acceptable patterns — choose one and be consistent within a feature.

### Manual try/catch (preferred for most features)

```dart
@override
Future<Either<Failure, Company>> getCompany(String id) async {
  try {
    final response = await remoteDataSource.getCompany(id);
    return Right(CompanyMapper.fromResponseToEntity(response));
  } on Exception catch (e, _) {
    qontakCommonDependency<QontakMonitor>().logCrashMonitor(
      logName: CompanyLogConstant.getCompany,
    );
    return Left(Failure(message: e.toString()));
  }
}
```

### TaskEither (FP style — used in newer feature packages)

```dart
@override
Future<Either<Failure, Company>> getCompany(String id) =>
    TaskEither.tryCatch(
      () => remoteDataSource.getCompany(id),
      (error, _) {
        qontakCommonDependency<QontakMonitor>().logCrashMonitor(
          logName: CompanyLogConstant.getCompany,
        );
        return Failure(message: error.toString());
      },
    ).map(CompanyMapper.fromResponseToEntity).run();
```

**Rules:**
- DataSources throw exceptions — never return `Either`
- Repositories catch at the boundary and return `Left(Failure(...))`
- Use cases pass through the `Either` — no additional catch
- `Right(null)` for void operations; prefer `const Right(null)`

---

## QontakMonitor Logging <!-- 15 -->

All repository and data source error paths log via `QontakMonitor`:

```dart
qontakCommonDependency<QontakMonitor>().logCrashMonitor(
  logName: CompanyLogConstant.getCompany,  // use a constant, not a raw string
);
```

Log name constants live in `features/<pkg>/lib/src/config/constants/`:

```dart
// features/crm_company/lib/src/config/constants/company_log_constant.dart
abstract class CompanyLogConstant {
  static const getCompany = 'CompanyRepository.getCompany';
  static const addCompany = 'CompanyRepository.addCompany';
  static const deleteCompany = 'CompanyRepository.deleteCompany';
}
```

**Rule:** Never use raw strings in production `logCrashMonitor` calls — always use a constant from the feature's logging constants file.

---

## BLoC Error Handling <!-- 15 -->

```dart
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
```

BLoCs never log to `QontakMonitor` — logging belongs at the repository boundary.

---

## Error Display in Screen <!-- 12 -->

```dart
BlocConsumer<CompanyBloc, CompanyState>(
  listenWhen: (prev, curr) =>
      prev.companyListState != curr.companyListState,
  listener: (context, state) {
    if (state.companyListState.status.isError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(state.companyListState.message ?? 'Something went wrong'),
        ),
      );
    }
  },
  buildWhen: (prev, curr) =>
      prev.companyListState != curr.companyListState,
  builder: (context, state) {
    if (state.companyListState.status.isError) {
      return Center(
        child: Text(state.companyListState.message ?? 'Failed'),
      );
    }
    // ...
  },
)
```

**Key:** Use `.status.isError` (not `.hasError`), `.status.isHasData` (not `.isLoaded`).
