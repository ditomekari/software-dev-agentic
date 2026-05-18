---
name: builder-data-create-repository-impl
description: Create a Repository implementation that bridges the domain interface with the DataSource and Mapper.
user-invocable: false
---

Create a RepositoryImpl following `.claude/reference/code-architecture/data-impl.md ## Repository Implementations section` and `.claude/reference/code-architecture/error-handling-impl.md`.

## Steps

1. **Grep** `.claude/reference/code-architecture/data-impl.md` for `## Repository Implementations`; only **Read** the full file if the section cannot be located
2. **Verify** all three dependencies exist: domain repository interface, datasource, mapper
3. **Locate** path: `lib/src/features/[feature]/data/repositories/`
4. **Create** `[feature]_repository_impl.dart`

## Repository Impl Pattern

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import '../../domain/entities/[feature]_entity.dart';
import '../../domain/errors/failure.dart';
import '../../domain/repositories/[feature]_repository.dart';
import '../datasources/[feature]_remote_data_source.dart';
import '../exceptions/app_exception.dart';
import '../mappers/[feature]_mapper.dart';

@LazySingleton(as: [Feature]Repository)
class [Feature]RepositoryImpl implements [Feature]Repository {
  [Feature]RepositoryImpl({
    required this.remoteDataSource,
    required this.mapper,
  });

  final [Feature]RemoteDataSource remoteDataSource;
  final [Feature]Mapper mapper;

  @override
  Future<Either<Failure, [Feature]Entity>> get[Feature](String id) async {
    try {
      final model = await remoteDataSource.get[Feature](id);
      return Right(mapper.toEntity(model));
    } on AppException catch (e) {
      return Left(e.toFailure());
    } catch (e) {
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }
}
```

## Output

Confirm file path and list all implemented methods with their try/catch structure confirmed.
