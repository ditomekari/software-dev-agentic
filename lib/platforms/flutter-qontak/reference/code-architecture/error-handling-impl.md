# Flutter Qontak — Error Handling

> Concepts and invariants: `lib/core/reference/code-architecture/error-handling-theory.md`. This file covers Dart syntax and patterns.

Errors flow inward: HTTP → `AppException` → `Failure` → `ViewDataState.error`. Each layer converts, never forwards raw exceptions.

---

## Error Flow <!-- 19 -->

```
HTTP / Storage / Parse error
        ↓
  DataSource throws AppException
  (via ErrorInterceptor or explicit throw)
        ↓
  RepositoryImpl catches → Left(failure)
        ↓
  UseCase passes through Either
        ↓
  BLoC: result.fold() → ViewDataState.error
        ↓
  Widget: state.hasError → shows ErrorView / SnackBar
```

---

## Error Boundaries <!-- 15 -->

| Boundary | Who converts | Result |
|---|---|---|
| HTTP error | `ErrorInterceptor` in `[prefix]_core` | `DioException.error = AppException` |
| DataSource → Repository | `catch (e on AppException)` in repository | `Left(e.toFailure())` |
| Any unexpected | `catch (e)` in repository | `Left(Failure.unknownFailure(...))` |

**Rules:**
- DataSources throw `AppException`, never return `Either`
- Repositories return `Either`, never throw
- Never let exceptions escape into domain or presentation

---

## Repository Error Handling <!-- 22 -->

The app-level repository pattern catches `Exception` (not `AppException`) and maps via `CoreMapperExceptionToFailure` (from `chat_core`):

```dart
// lib/data/repositories/product_tour_repositories.dart
class ProductTourRepositoryImpl implements ProductTourRepository {
  ProductTourRepositoryImpl({required this.localDataSource});
  final ProductTourLocalDataSource localDataSource;

  @override
  Future<Either<Failure, bool>> getFirstRun() async {
    try {
      return Right(await localDataSource.getFirstRun());
    } on Exception catch (error) {
      return Left(
        CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error),
      );
    }
  }

  @override
  Future<Either<Failure, bool>> setFirstRun() async {
    try {
      return Right(await localDataSource.setFirstRun());
    } on Exception catch (error) {
      return Left(
        CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error),
      );
    }
  }
}
```

Use `CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error)` from `chat_core` instead of a custom `AppException.toFailure()` extension.

---

## BLoC Error Handling <!-- 20 -->

```dart
// Actual pattern from LoginBloc
final result = await getSSOTokenUseCase.call(
  GetSSOTokenUseCaseParams(ssoCode: event.ssoCode),
);

result.fold(
  (failure) => emit(state.copyWith(
    loginState: ViewDataState.error(
      message: failure.message,  // Failure exposes .message directly
      failure: failure,
    ),
  )),
  (success) => emit(state.copyWith(
    loginState: ViewDataState.loaded(data: success),
  )),
);
```

Use `failure.message` directly — do not call `failure.when(...)` unless you need to branch on failure subtypes for different UI treatment.

---

## Validation Errors (HTTP 422) <!-- 36 -->

```dart
// In ErrorInterceptor
if (statusCode == 422) {
  final errors = (responseData?['errors'] as Map<String, dynamic>?);
  throw AppException.validation(
    message: responseData?['message'] as String? ?? 'Validation failed',
    errors: errors,
    statusCode: 422,
  );
}
```

```dart
// In BLoC — extract field-level errors
result.fold(
  (failure) {
    if (failure is ValidationFailure) {
      final fieldErrors = failure.errors as Map<String, dynamic>?;
      emit(state.copyWith(
        submitState: ViewDataState.error(message: failure.message, failure: failure),
        fieldErrors: fieldErrors,
      ));
    } else {
      emit(state.copyWith(
        submitState: ViewDataState.error(message: failure.message, failure: failure),
      ));
    }
  },
  (_) => emit(state.copyWith(submitState: ViewDataState.loaded())),
);
```

---

## ErrorInterceptor (in `[prefix]_core`) <!-- 34 -->

```dart
// shared/[prefix]_core/lib/src/network/error_interceptor.dart
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final exception = switch (err.type) {
      DioExceptionType.connectionError ||
      DioExceptionType.connectionTimeout ||
      DioExceptionType.receiveTimeout =>
        AppException.network(message: 'No internet connection'),
      DioExceptionType.badResponse => _mapStatusCode(err),
      _ => AppException.unknown(message: err.message ?? 'Unknown error'),
    };
    handler.reject(
      DioException(requestOptions: err.requestOptions, error: exception),
    );
  }

  AppException _mapStatusCode(DioException err) {
    final statusCode = err.response?.statusCode ?? 0;
    final message =
        (err.response?.data as Map<String, dynamic>?)?['message'] as String? ??
        err.message ?? 'Server error';
    return statusCode == 422
        ? AppException.validation(message: message, statusCode: statusCode)
        : AppException.server(message: message, statusCode: statusCode);
  }
}
```

---

## Error UI Patterns <!-- 26 -->

```dart
// Inline in BlocBuilder — blocking error
if (state.dataState.hasError) {
  return ErrorView(
    message: state.dataState.message ?? 'Something went wrong',
    onRetry: () => context.read<InboxBloc>().add(const InboxEvent.loadInbox()),
  );
}

// Toast via BlocListener — non-blocking error
BlocListener<InboxBloc, InboxState>(
  listenWhen: (prev, curr) =>
      prev.markReadState != curr.markReadState && curr.markReadState.hasError,
  listener: (context, state) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(state.markReadState.message ?? 'Failed')),
    );
  },
  child: ...,
)
```

---

## Global Error Boundary <!-- 23 -->

The global error boundary lives in `engine.dart`, wrapping the entire startup sequence:

```dart
// lib/engine.dart
void start({EnvType envType = EnvType.staging}) =>
    runZonedGuarded<Future<void>>(
      () async {
        WidgetsFlutterBinding.ensureInitialized();
        // ... init (Firebase, DI, etc.)

        FlutterError.onError = (errorDetails) {
          FirebaseCrashlytics.instance.recordFlutterFatalError(errorDetails);
        };
        PlatformDispatcher.instance.onError = (error, stack) {
          FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
          return true;
        };
        FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;

        runApp(AppProvider(child: App(environment: envType.name)));
      },
      (error, stack) => FirebaseCrashlytics.instance.recordError(error, stack),
    );
```
```

---

## Layer Invariants <!-- 7 -->

- DataSources throw `AppException` — they never return `Either` to signal failure
- Repository implementations always catch and return `Left(Failure)` — no `AppException` propagates to use cases
- Use cases propagate `Either<Failure, T>` unchanged — they do not re-map failures
- BLoCs catch all `Either` results from use cases via `result.fold()` — no unhandled exception reaches the widget tree
- Widgets never inspect `Failure` subtypes directly — they render the `ViewDataState` the BLoC emits
