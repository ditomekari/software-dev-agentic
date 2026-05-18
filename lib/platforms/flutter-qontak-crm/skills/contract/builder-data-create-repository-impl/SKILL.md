---
name: builder-data-create-repository-impl
description: Create a Repository implementation for Flutter Qontak CRM that bridges the domain interface with DataSource and Mapper. Uses TaskEither.tryCatch or manual try/catch returning Either.
user-invocable: false
---

Create a RepositoryImpl following `lib/platforms/flutter-qontak-crm/reference/code-architecture/data-impl.md ## Repository Implementation`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak-crm/reference/code-architecture/data-impl.md` for `## Repository Implementation`; only **Read** the full file if the section cannot be located
2. **Verify** all three dependencies exist: domain repository interface, datasource, mapper
3. **Locate** path: `features/[prefix]_[feature]/lib/src/data/repositories/`
4. **Create** `[feature]_repository_impl.dart`

## Repository Impl Pattern (manual try/catch — preferred for new code)

```dart
// features/[prefix]_[feature]/lib/src/data/repositories/[feature]_repository_impl.dart
import 'package:fpdart/fpdart.dart';
import 'package:qontak_common/qontak_common.dart'; // Failure
import 'package:[prefix]_[feature]/src/domain/entities/[concept].dart';
import 'package:[prefix]_[feature]/src/domain/repositories/[feature]_repository.dart';
import '../data_sources/remote/[feature]_remote_data_source.dart';
import '../mappers/[feature]_mapper.dart';

// No @LazySingleton — registration is manual in Qontak[Feature]Dependency
class [Feature]RepositoryImpl implements [Feature]Repository {
  [Feature]RepositoryImpl({
    required this.remoteDataSource,
  });

  final [Feature]RemoteDataSource remoteDataSource;

  @override
  Future<Either<Failure, [Concept]>> get[Concept](String id) async {
    try {
      final response = await remoteDataSource.get[Concept](id);
      return Right([Feature]Mapper.fromResponseToEntity(response));
    } on Exception catch (e, s) {
      qontakCommonDependency<QontakMonitor>().logCrashMonitor(
        logName: [Feature]LogConstant.get[Concept],
      );
      return Left(Failure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> delete[Concept](String id) async {
    try {
      await remoteDataSource.delete[Concept](id);
      return const Right(null);
    } on Exception catch (e, s) {
      qontakCommonDependency<QontakMonitor>().logCrashMonitor(
        logName: [Feature]LogConstant.delete[Concept],
      );
      return Left(Failure(message: e.toString()));
    }
  }
}
```

## Repository Impl Pattern (TaskEither — FP style, used in newer feature packages)

```dart
@override
Future<Either<Failure, [Concept]>> get[Concept](String id) =>
    TaskEither.tryCatch(
      () => remoteDataSource.get[Concept](id),
      (error, _) => Failure(message: error.toString()),
    ).map([Feature]Mapper.fromResponseToEntity).run();
```

## DI Registration (caller adds to Qontak[Feature]Dependency)

```dart
// In Qontak[Feature]Dependency._register[Feature]Domain():
qontak[Feature]Dependency.registerLazySingleton<[Feature]Repository>(
  () => [Feature]RepositoryImpl(remoteDataSource: qontak[Feature]Dependency()),
);
```

## Rules

- No `@LazySingleton` annotation — registration is manual in the feature DI class
- Registered as the abstract type: `registerLazySingleton<[Feature]Repository>(() => [Feature]RepositoryImpl(...))`
- Static mapper methods (`[Feature]Mapper.fromResponseToEntity(response)`) — no mapper instance injection needed
- `Right(null)` for void return; `const Right(null)` preferred
- Log via `QontakMonitor.logCrashMonitor` in error handlers using a constant from the feature's logging constants file
- `TaskEither.tryCatch` or manual try/catch are both acceptable — be consistent within a feature

## Output

Confirm file path and list all implemented methods with error-handling structure confirmed.
