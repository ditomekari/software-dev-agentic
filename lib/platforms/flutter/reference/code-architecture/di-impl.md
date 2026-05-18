# Flutter — Dependency Injection

> Concepts and invariants: `reference/code-architecture/di-theory.md`. This file covers Dart syntax and Flutter-specific patterns.

`get_it` for the service locator. `injectable` for annotation-driven code generation. One DI module per feature.

---

## Setup <!-- 15 -->

```yaml
# pubspec.yaml
dependencies:
  get_it: ^7.6.0
  injectable: ^2.5.0

dev_dependencies:
  injectable_generator: ^2.6.0
  build_runner: ^2.4.0
```

---

## Global Locator <!-- 23 -->

```dart
// di/injection.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

import 'injection.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async => getIt.init();
```

Generate after adding/changing annotations:

```bash
dart run build_runner build --delete-conflicting-outputs
```

---

## Annotations <!-- 12 -->

| Annotation | Lifecycle | Use For |
|------------|-----------|---------|
| `@lazySingleton` | Singleton, created on first access | Repositories, use cases, mappers, datasources |
| `@singleton` | Singleton, created at startup | Core services (auth, analytics) |
| `@injectable` | New instance each time `getIt.get()` is called | BLoCs, Cubits |
| `@LazySingleton(as: Interface)` | Singleton bound to interface | Repository/datasource implementations |
| `@module` | Abstract class providing external dependencies | Dio, SharedPreferences, etc. |

---

## Feature DI Module <!-- 21 -->

Each feature owns its DI registration. Scope all registrations to the feature's directory.

```dart
// features/employee/di/employee_module.dart
import 'package:injectable/injectable.dart';
import 'package:get_it/get_it.dart';

@InjectableInit(
  generateForDir: ['lib/src/features/employee'],
  preferRelativeImports: true,
)
Future<GetIt> configureEmployeeDependencies() async =>
    GetIt.instance.init();
```

Or use the global `@InjectableInit` and annotate each class in the feature folder.

---

## Registering Classes <!-- 51 -->

### Repositories and Use Cases

```dart
// Use @LazySingleton(as:) to bind implementation to interface
@LazySingleton(as: EmployeeRepository)
class EmployeeRepositoryImpl implements EmployeeRepository {
  EmployeeRepositoryImpl({required this.remoteDataSource, required this.mapper});
  // ...
}

// Use @lazySingleton for concrete classes (mappers, use cases)
@lazySingleton
class EmployeeMapper extends BaseMapper<EmployeeModel, EmployeeEntity> {
  // ...
}

@lazySingleton
class GetEmployeeUseCase implements UseCase<EmployeeEntity, String> {
  GetEmployeeUseCase({required this.repository});
  final EmployeeRepository repository;
  // ...
}
```

### BLoCs (New Instance Per Screen)

```dart
@injectable
class EmployeeBloc extends Bloc<EmployeeEvent, EmployeeState> {
  EmployeeBloc({
    required this.getEmployeeUseCase,
    required this.updateEmployeeUseCase,
  }) : super(EmployeeState.initial()) { ... }
  // ...
}
```

Provide via `BlocProvider`:

```dart
BlocProvider(
  create: (_) => getIt<EmployeeBloc>()
    ..add(EmployeeEvent.loadEmployee(employeeId: id)),
  child: const EmployeeView(),
)
```

---

## External Dependencies Module <!-- 35 -->

Register third-party instances (Dio, SharedPreferences) via `@module`:

```dart
// di/app_module.dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:shared_preferences/shared_preferences.dart';

@module
abstract class AppModule {
  @lazySingleton
  Dio get dio => Dio(BaseOptions(
        baseUrl: const String.fromEnvironment(
          'API_BASE_URL',
          defaultValue: 'https://api.example.com',
        ),
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
      ))
        ..interceptors.addAll([
          ErrorInterceptor(),
          LogInterceptor(logPrint: (obj) => debugPrint(obj.toString())),
        ]);

  @preResolve
  Future<SharedPreferences> get prefs => SharedPreferences.getInstance();
}
```

`@preResolve` tells injectable to await the future before resolving.

---

## Environment-Based Registration <!-- 30 -->

```dart
@module
abstract class NetworkModule {
  @lazySingleton
  @prod
  Dio get prodDio => Dio(BaseOptions(baseUrl: 'https://api.example.com'));

  @lazySingleton
  @dev
  Dio get devDio => Dio(BaseOptions(baseUrl: 'https://api.staging.example.com'));
}
```

Configure at app startup:

```dart
// main.dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDependencies(
    environment: const String.fromEnvironment('ENV', defaultValue: 'prod'),
  );
  runApp(const App());
}
```

---

## DI Principles <!-- 13 -->

| Component | Lifecycle | Why |
|-----------|-----------|-----|
| DataSources | `@lazySingleton` | Stateless, expensive to create |
| Mappers | `@lazySingleton` | Stateless, pure functions |
| Repositories | `@lazySingleton` | Stateless, bound to interface |
| Use Cases | `@lazySingleton` | Stateless, depend on singletons |
| BLoCs | `@injectable` | Stateful, one per screen |
| Cubits | `@lazySingleton` or `@injectable` | Depends on whether state is shared |

---

## Testing with getIt <!-- 27 -->

Override registrations in tests by unregistering and re-registering:

```dart
setUp(() {
  getIt.reset();
  getIt.registerLazySingleton<EmployeeRepository>(
    () => MockEmployeeRepository(),
  );
  getIt.registerFactory<EmployeeBloc>(
    () => EmployeeBloc(
      getEmployeeUseCase: MockGetEmployeeUseCase(),
      updateEmployeeUseCase: MockUpdateEmployeeUseCase(),
    ),
  );
});
```

Or prefer constructor injection in tests — pass mocks directly without getIt:

```dart
final bloc = EmployeeBloc(
  getEmployeeUseCase: mockGetEmployeeUseCase,
  updateEmployeeUseCase: mockUpdateEmployeeUseCase,
);
```
