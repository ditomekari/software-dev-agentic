# Flutter — Error Handling

> Concepts and invariants: `reference/code-architecture/error-handling-theory.md`. This file covers Dart syntax and Flutter-specific patterns.

Errors flow inward: HTTP → `AppException` → `Failure` → `ViewDataState.error`. Each layer converts, never forwards raw exceptions.

---

## Error Flow <!-- 21 -->

```
HTTP / Storage / Parse error
          ↓
  Data layer throws AppException
  (in datasource or interceptor)
          ↓
  Repository catches, converts to Failure
  returns Left(failure)
          ↓
  UseCase passes through Either
          ↓
  BLoC calls result.fold()
  emits ViewDataState.error(message, failure)
          ↓
  Widget reads state.hasError, shows UI
```

---

## Error Types <!-- 30 -->

The canonical error type. Lives in `domain/errors/failure.dart`. See `domain.md` for the full definition.

```dart
// Accessing failure data in a BLoC
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
      dataState: ViewDataState.error(
        message: message,
        failure: failure,
      ),
    ));
  },
  (data) => emit(state.copyWith(
    dataState: ViewDataState.loaded(data: data),
  )),
);
```

---

## Error Mapping <!-- 13 -->

Errors are converted at two boundaries:

| Boundary | Conversion |
|---|---|
| HTTP → DataSource | `ErrorInterceptor` catches `DioException`, attaches `AppException` as the error |
| DataSource → Repository | `catch (e on AppException)` → `Left(e.toFailure())` |

See `## AppException (Data)` and `## HTTP Error Interceptor` sections for code patterns.

---

## AppException (Data) <!-- 40 -->

Typed exceptions thrown inside datasources. Lives in `data/exceptions/app_exception.dart`. See `data.md` for the full definition and `toFailure()` extension.

### Throwing in DataSources

DataSources only throw — they never return `Either`. The repository catches and converts.

```dart
// In a datasource implementation
Future<EmployeeModel> getEmployee(String id) async {
  final response = await dio.get('/api/v1/employees/$id');
  final data = response.data as Map<String, dynamic>?;
  if (data == null || data['data'] == null) {
    throw AppException.server(
      message: 'Employee not found',
      statusCode: 404,
    );
  }
  return EmployeeModel.fromJson(data['data'] as Map<String, dynamic>);
}
```

### Catching in Repositories

```dart
try {
  final model = await remoteDataSource.getEmployee(id);
  return Right(mapper.toEntity(model));
} on AppException catch (e) {
  return Left(e.toFailure());   // typed conversion
} catch (e, stackTrace) {
  // Log unexpected errors
  debugPrint('Unexpected: $e\n$stackTrace');
  return Left(Failure.unknownFailure(message: e.toString()));
}
```

---

## HTTP Error Interceptor <!-- 15 -->

Converts Dio network errors into `AppException` before they reach repositories. See `data.md` for the full `ErrorInterceptor`.

Register it when creating Dio:

```dart
Dio(BaseOptions(baseUrl: '...'))
  ..interceptors.add(ErrorInterceptor());
```

After the interceptor runs, all Dio errors that escape as `DioException` have an `AppException` as their `error` property. The repository `catch (e)` clause handles them.

---

## Validation Errors <!-- 44 -->

API validation errors (HTTP 422) carry structured field errors.

```dart
// In the error interceptor
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
// In the BLoC, read field-level errors from the failure
result.fold(
  (failure) {
    if (failure is ValidationFailure) {
      final fieldErrors = failure.errors as Map<String, dynamic>?;
      emit(state.copyWith(
        submitState: ViewDataState.error(
          message: failure.message,
          failure: failure,
        ),
        fieldErrors: fieldErrors,
      ));
    } else {
      emit(state.copyWith(
        submitState: ViewDataState.error(
          message: failure.message ?? 'Failed',
          failure: failure,
        ),
      ));
    }
  },
  (_) => emit(state.copyWith(submitState: ViewDataState.loaded())),
);
```

---

## Error UI <!-- 39 -->

Standard patterns for surfacing errors:

```dart
// Inline error in BlocBuilder
builder: (context, state) {
  if (state.dataState.hasError) {
    return ErrorView(
      message: state.dataState.message ?? 'Something went wrong',
      onRetry: () => context
          .read<EmployeeBloc>()
          .add(const EmployeeEvent.refreshEmployee()),
    );
  }
  // ...
}
```

```dart
// Toast / SnackBar via BlocListener for non-blocking errors
BlocListener<EmployeeBloc, EmployeeState>(
  listenWhen: (prev, curr) =>
      prev.submitState != curr.submitState &&
      curr.submitState.hasError,
  listener: (context, state) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(state.submitState.message ?? 'Failed'),
        backgroundColor: Colors.red,
      ),
    );
  },
  child: ...,
)
```

---

## Global Error Boundary (Optional) <!-- 26 -->

Catch uncaught Flutter and Dart errors at app level:

```dart
// main.dart
void main() {
  runZonedGuarded(
    () async {
      WidgetsFlutterBinding.ensureInitialized();
      FlutterError.onError = (details) {
        // Send to crash reporting (Firebase Crashlytics, Sentry, etc.)
        debugPrint('Flutter error: ${details.exception}');
      };
      await configureDependencies();
      runApp(const App());
    },
    (error, stack) {
      debugPrint('Unhandled error: $error\n$stack');
    },
  );
}
```

---

## Rules <!-- 8 -->

1. **DataSources throw, Repositories return Either** — never mix
2. **Never throw in domain or presentation** — only `Left(failure)` and `emit(...error...)`
3. **Always handle both fold arms** — never `result.getOrElse(() => throw ...)`
4. **Log unexpected errors** in the repository catch-all before wrapping as `unknownFailure`
5. **Keep user messages short** — technical details go in `developerMessage`, not `message`
6. **Field validation errors** use `ValidationFailure` — never encode field names in `message`
