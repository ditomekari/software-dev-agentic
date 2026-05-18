---
name: flutter-qontak-crm-add-repository
description: Add a repository interface, repository implementation, and data source(s) to a Qontak CRM feature package.
user-invocable: false
---

## Steps

### 1 — Create the domain repository interface

`features/crm_<domain>/lib/src/domain/repositories/<name>_repository.dart`:

```dart
import 'package:crm_core/crm_dependency.dart' hide Failure;
import 'package:crm_core/qontak_common.dart';
import 'package:crm_<domain>/src/domain/entities/<entity>/<entity>.dart';

abstract class <Name>Repository {
  Future<Either<Failure, <Entity>>> get<Entity>ById({required String id});
  Future<Either<Failure, <Entity>>> add<Entity>({required <Entity> request});
  Future<Either<Failure, <Entity>>> edit<Entity>({
    required String id,
    required <Entity> request,
  });
  Future<Either<Failure, bool>> delete<Entity>ById({required String id});
}
```

Rules:
- All methods return `Future<Either<Failure, T>>`.
- Parameters use domain entities only — never models or DTOs.
- Add to `lib/src/domain/repositories/repositories.dart` barrel.

### 2 — Create the remote data source

`features/crm_<domain>/lib/src/data/data_sources/remote/<name>_remote_data_source.dart`:

```dart
import 'dart:async';

import 'package:crm_core/qontak_common.dart' hide Endpoint;
import 'package:crm_<domain>/src/config/constants/endpoint.dart';
import 'package:crm_<domain>/src/data/models/remote/<name>_response/<name>_response.dart';

abstract class <Name>RemoteDataSource {
  Future<BaseResponse<<Name>Response>> get<Name>ById({required String id});
  Future<BaseResponse<<Name>Response>> add<Name>({required <Name>Response request});
  Future<BaseResponse<<Name>Response>> edit<Name>({
    required String id,
    required <Name>Response request,
  });
  Future<BaseResponse<Object?>> delete<Name>ById({required String id});
}

class <Name>RemoteDataSourceImpl implements <Name>RemoteDataSource {
  const <Name>RemoteDataSourceImpl({required this.baseApi});
  final BaseApi baseApi;

  @override
  Future<BaseResponse<<Name>Response>> get<Name>ById({required String id}) async {
    unawaited(
      qontakCommonDependency<QontakMonitor>()
          .logCrashMonitor(logName: remote<Name>DatasourceGet<Name>ById),
    );
    final response = await baseApi.get(Endpoint.<name>ById(id: id));
    return BaseResponse<<Name>Response>.fromJson(
      response,
      onDeserializedT: (r) => <Name>Response.fromJson(r),
    );
  }

  @override
  Future<BaseResponse<<Name>Response>> add<Name>({
    required <Name>Response request,
  }) async {
    unawaited(
      qontakCommonDependency<QontakMonitor>()
          .logCrashMonitor(logName: remote<Name>DatasourceAdd<Name>),
    );
    final response = await baseApi.post(Endpoint.<name>, body: request.toJson());
    return BaseResponse<<Name>Response>.fromJson(
      response,
      onDeserializedT: (r) => <Name>Response.fromJson(r),
    );
  }

  @override
  Future<BaseResponse<<Name>Response>> edit<Name>({
    required String id,
    required <Name>Response request,
  }) async {
    unawaited(
      qontakCommonDependency<QontakMonitor>()
          .logCrashMonitor(logName: remote<Name>DatasourceEdit<Name>),
    );
    final response = await baseApi.put(Endpoint.<name>ById(id: id), body: request.toJson());
    return BaseResponse<<Name>Response>.fromJson(
      response,
      onDeserializedT: (r) => <Name>Response.fromJson(r),
    );
  }

  @override
  Future<BaseResponse<Object?>> delete<Name>ById({required String id}) async {
    unawaited(
      qontakCommonDependency<QontakMonitor>()
          .logCrashMonitor(logName: remote<Name>DatasourceDelete<Name>ById),
    );
    final response = await baseApi.delete(Endpoint.<name>ById(id: id));
    return BaseResponse.fromJson(response, onDeserializedT: (r) => r);
  }
}
```

Add logging constants to `lib/src/config/constants/logging/<name>_logging_constants.dart`:
```dart
const remote<Name>DatasourceGet<Name>ById = 'remote_<name>_datasource_get_<name>_by_id';
const remote<Name>DatasourceAdd<Name> = 'remote_<name>_datasource_add_<name>';
// ...
```

### 3 — (Optional) Create a local data source for offline support

`features/crm_<domain>/lib/src/data/data_sources/local/<name>_local_data_source.dart`:

```dart
import 'package:crm_core/qontak_common.dart';
import 'package:crm_<domain>/src/data/models/local/<name>/<name>_db.dart';

abstract class <Name>LocalDataSource {
  Future<List<<Name>Db>> getAll<Name>s();
  Future<<Name>Db> add<Name>({required <Name>Db request});
  Future<void> removeAll<Name>s();
}

class <Name>LocalDataSourceImpl implements <Name>LocalDataSource {
  const <Name>LocalDataSourceImpl({required this.databaseService});
  final DatabaseService databaseService;

  @override
  Future<List<<Name>Db>> getAll<Name>s() async {
    final isar = await databaseService.database;
    return isar.<name>Dbs.where().findAll();
  }
  // ... other methods
}
```

### 4 — Create the remote API response model

`features/crm_<domain>/lib/src/data/models/remote/<name>_response/<name>_response.dart`:

```dart
import 'package:crm_core/crm_dependency.dart';

part '<name>_response.freezed.dart';
part '<name>_response.g.dart';

@freezed
class <Name>Response with _$<Name>Response {
  const factory <Name>Response({
    @JsonKey(name: 'id') String? id,
    @JsonKey(name: 'name') String? name,
    // map every API field with @JsonKey(name: 'snake_case')
  }) = _<Name>Response;

  factory <Name>Response.fromJson(Map<String, dynamic> json) =>
      _$<Name>ResponseFromJson(json);
}
```

### 5 — Create the mapper

`features/crm_<domain>/lib/src/data/mappers/<name>_mapper.dart`:

```dart
import 'package:crm_<domain>/src/data/models/remote/<name>_response/<name>_response.dart';
import 'package:crm_<domain>/src/domain/entities/<entity>/<entity>.dart';

class <Name>Mapper {
  static <Entity> fromResponseToEntity({required <Name>Response? source}) =>
      <Entity>(
        id: source?.id ?? '',
        name: source?.name ?? '',
      );

  static <Name>Response fromEntityToResponse({required <Entity> source}) =>
      <Name>Response(
        id: source.id,
        name: source.name,
      );
}
```

### 6 — Implement the repository

`features/crm_<domain>/lib/src/data/repositories/<name>_repository_impl.dart`:

```dart
import 'dart:async';

import 'package:crm_core/crm_dependency.dart' hide Failure;
import 'package:crm_core/qontak_common.dart';
import 'package:crm_<domain>/src/crm_<domain>.dart';

class <Name>RepositoryImpl implements <Name>Repository {
  const <Name>RepositoryImpl({required this.<name>RemoteDataSource});

  final <Name>RemoteDataSource <name>RemoteDataSource;

  @override
  Future<Either<Failure, <Entity>>> get<Entity>ById({
    required String id,
  }) =>
      TaskEither.tryCatch(
        () async {
          unawaited(
            qontakCommonDependency<QontakMonitor>()
                .logCrashMonitor(logName: <name>RepoGet<Entity>ById),
          );
          final result = await <name>RemoteDataSource.get<Name>ById(id: id);
          return <Name>Mapper.fromResponseToEntity(source: result.response);
        },
        (error, _) => CoreMapperExceptionToFailure.mapExceptionToFailure(error: error),
      ).run();

  @override
  Future<Either<Failure, <Entity>>> add<Entity>({required <Entity> request}) =>
      TaskEither.tryCatch(
        () async {
          unawaited(
            qontakCommonDependency<QontakMonitor>()
                .logCrashMonitor(logName: <name>RepoAdd<Entity>),
          );
          final result = await <name>RemoteDataSource.add<Name>(
            request: <Name>Mapper.fromEntityToResponse(source: request),
          );
          return <Name>Mapper.fromResponseToEntity(source: result.response);
        },
        (error, _) => CoreMapperExceptionToFailure.mapExceptionToFailure(error: error),
      ).run();

  // ... remaining methods follow the same TaskEither pattern
}
```

Add repo logging constants to the logging constants file:
```dart
const <name>RepoGet<Entity>ById = '<name>_repo_get_<entity>_by_id';
```

### 7 — Register in DI

In `lib/src/config/di/qontak_<domain>_dependency.dart`, in `_register<Domain>Data()`:

```dart
qontak<Domain>Dependency
  ..registerLazySingleton<<Name>RemoteDataSource>(
    () => <Name>RemoteDataSourceImpl(baseApi: qontakCommonDependency()),
  )
  ..registerLazySingleton<<Name>Repository>(
    () => <Name>RepositoryImpl(<name>RemoteDataSource: qontak<Domain>Dependency()),
  );
```

### 8 — Run code generation

```bash
cd features/crm_<domain>
dart run build_runner build --delete-conflicting-outputs
```
