---
name: builder-data-create-repository-impl
description: Create a Repository implementation for Flutter Qontak that bridges the domain interface with the DataSource and Mapper. Uses CoreMapperExceptionToFailure, not AppException.toFailure().
user-invocable: false
---

Create a RepositoryImpl following `lib/platforms/flutter-qontak/reference/code-architecture/data-impl.md ## Repository Implementation section` and `lib/platforms/flutter-qontak/reference/code-architecture/error-handling-impl.md ## Repository Error Handling section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/data-impl.md` for `## Repository Implementation`; only **Read** the full file if the section cannot be located
2. **Verify** all three dependencies exist: domain repository interface, datasource, mapper
3. **Locate** path: `features/[prefix]_[feature]/lib/src/data/repositories/`
4. **Create** `[feature]_repository_impl.dart`

## Repository Impl Pattern

```dart
// features/[prefix]_[feature]/lib/src/data/repositories/[feature]_repository_impl.dart
import 'package:fpdart/fpdart.dart';
import 'package:[prefix]_core/[prefix]_core.dart'; // re-exports Failure, CoreMapperExceptionToFailure
import 'package:[prefix]_[feature]/src/domain/entities/[concept].dart';
import 'package:[prefix]_[feature]/src/domain/repositories/[feature]_repository.dart';
import '../datasources/[feature]_remote_data_source.dart';
import '../mappers/[concept]_mapper.dart';

// No @LazySingleton — registration is manual in [Feature]Dependency._registerDomain()
class [Feature]RepositoryImpl implements [Feature]Repository {
  [Feature]RepositoryImpl({
    required this.remoteDataSource,
  });

  final [Feature]RemoteDataSource remoteDataSource;

  @override
  Future<Either<Failure, [Concept]>> get[Concept](String id) async {
    try {
      final response = await remoteDataSource.get[Concept](id);
      return Right([Concept]Mapper.fromResponseToEntity(response));
    } on Exception catch (error) {
      return Left(
        CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error),
      );
    }
  }

  @override
  Future<Either<Failure, void>> delete[Concept](String id) async {
    try {
      await remoteDataSource.delete[Concept](id);
      return const Right(null);
    } on Exception catch (error) {
      return Left(
        CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error),
      );
    }
  }
}
```

## DI Registration (caller adds to [Feature]Dependency)

```dart
// In [Feature]Dependency._registerDomain():
[feature]Dependency.registerLazySingleton<[Feature]Repository>(
  () => [Feature]RepositoryImpl(remoteDataSource: [feature]Dependency()),
);
```

## Rules

- Catch `Exception` (not `AppException`) — use `CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error)` from `chat_core`
- Never use `AppException.toFailure()` extension — that is the generic flutter pattern, not Qontak
- No `@LazySingleton` annotation — registration is manual in the feature DI class
- Registered as the abstract type: `registerLazySingleton<[Feature]Repository>(() => [Feature]RepositoryImpl(...))`
- Static mapper methods (`[Concept]Mapper.fromResponseToEntity(response)`) — no mapper instance injection needed
- `Right(null)` for void return; `const Right(null)` preferred

## Output

Confirm file path and list all implemented methods with error-handling structure confirmed.
