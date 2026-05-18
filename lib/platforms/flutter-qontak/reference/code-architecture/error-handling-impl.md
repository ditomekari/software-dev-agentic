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

## Repository Error Handling <!-- 19 -->

```dart
@override
Future<Either<Failure, User>> getCurrentUser() async {
  try {
    final response = await _remoteDataSource.getCurrentUser();
    return Right(UserMapper.fromResponseToEntity(response));
  } on AppException catch (e) {
    return Left(e.toFailure());
  } catch (e, stackTrace) {
    debugPrint('Unexpected error in getCurrentUser: $e\n$stackTrace');
    return Left(Failure.unknownFailure(message: e.toString()));
  }
}
```

---

## BLoC Error Handling <!-- 26 -->

```dart
final result = await _login(LoginParams(email: event.email, password: event.password));

result.fold(
  (failure) {
    final message = failure.when(
      serverFailure: (msg, _, __, ___) => msg,
      validationFailure: (msg, __, ___) => msg,
      networkFailure: (msg) => msg,
      unknownFailure: (msg) => msg,
      localFailure: (msg) => msg,
    );
    emit(state.copyWith(
      loginState: ViewDataState.error(message: message, failure: failure),
    ));
  },
  (user) => emit(state.copyWith(
    loginState: ViewDataState.loaded(data: user),
  )),
);
```

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

## Global Error Boundary <!-- 20 -->

```dart
// main.dart
void main() {
  runZonedGuarded(
    () async {
      WidgetsFlutterBinding.ensureInitialized();
      FlutterError.onError = (details) {
        FirebaseCrashlytics.instance.recordFlutterFatalError(details);
      };
      await configureDependencies();
      runApp(const App());
    },
    (error, stack) {
      FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    },
  );
}
```
