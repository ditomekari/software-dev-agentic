# Flutter — Data Layer

> Concepts and invariants: `reference/code-architecture/data-theory.md`. This file covers Dart syntax and Flutter-specific patterns.

Implements repository interfaces from the Domain layer. Knows about serialization, HTTP, local storage, and mappers. Never leaks into Domain or Presentation.

---

## DTOs <!-- 35 -->

DTO classes for API responses. **Always have `fromJson` — entities never do.**

```dart
// data/models/employee_model.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'employee_model.freezed.dart';
part 'employee_model.g.dart';

@freezed
class EmployeeModel with _$EmployeeModel {
  const factory EmployeeModel({
    @JsonKey(name: 'employee_id') String? id,
    @JsonKey(name: 'full_name') String? name,
    String? email,
    @JsonKey(name: 'join_date') String? joinDate,
    @JsonKey(name: 'department_id') String? departmentId,
  }) = _EmployeeModel;

  factory EmployeeModel.fromJson(Map<String, dynamic> json) =>
      _$EmployeeModelFromJson(json);
}
```

**Rules:**
- Both `.freezed.dart` and `.g.dart` parts
- All fields nullable — API data is untrusted
- `@JsonKey(name:)` for snake_case → camelCase mapping
- No business logic
- Never returned from repository — always mapped to entity first

---

## Payload (Write Models) <!-- 53 -->

Separate class for request bodies. Keeps read models clean.

```dart
// data/models/update_employee_payload.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'update_employee_payload.freezed.dart';
part 'update_employee_payload.g.dart';

@freezed
class UpdateEmployeePayload with _$UpdateEmployeePayload {
  const factory UpdateEmployeePayload({
    @JsonKey(name: 'full_name') required String name,
    required String email,
    @JsonKey(name: 'department_id') String? departmentId,
  }) = _UpdateEmployeePayload;

  factory UpdateEmployeePayload.fromJson(Map<String, dynamic> json) =>
      _$UpdateEmployeePayloadFromJson(json);
}
```

**Domain Params → Data Payload flow:**

```
Domain Params (pure Dart)
      ↓
Repository Impl converts
      ↓
Data Payload (@JsonKey, freezed, .toJson())
      ↓
DataSource sends to API
```

Simple conversions can happen inline in the repository. Complex conversions warrant a `PayloadMapper`:

```dart
// data/mappers/update_employee_payload_mapper.dart
@lazySingleton
class UpdateEmployeePayloadMapper {
  UpdateEmployeePayload fromParams(UpdateEmployeeParams params) =>
      UpdateEmployeePayload(
        name: params.name,
        email: params.email,
        departmentId: params.departmentId,
      );
}
```

---

## Mappers <!-- 44 -->

Convert Models → Entities. One mapper per aggregate root.

### BaseMapper Contract

```dart
// data/mappers/base_mapper.dart
abstract class BaseMapper<Model, Entity> {
  Entity toEntity(Model model);
}
```

### Mapper Implementation

```dart
// data/mappers/employee_mapper.dart
import 'package:injectable/injectable.dart';
import '../../domain/entities/employee_entity.dart';
import '../models/employee_model.dart';
import 'base_mapper.dart';

@lazySingleton
class EmployeeMapper extends BaseMapper<EmployeeModel, EmployeeEntity> {
  @override
  EmployeeEntity toEntity(EmployeeModel model) => EmployeeEntity(
        id: model.id ?? '',
        name: model.name ?? '',
        email: model.email ?? '',
        joinDate: model.joinDate != null
            ? DateTime.tryParse(model.joinDate!)
            : null,
      );
}
```

**Rules:**
- One mapper per entity type
- Handle nulls with explicit defaults — never assume API fields are present
- Date strings → `DateTime` conversion happens in mapper, not entity
- List mappers call `toEntity` per item: `models.map(mapper.toEntity).toList()`

---

## Data Sources <!-- 127 -->

Separate remote and local data sources via abstract interface + implementation.

### Remote DataSource

```dart
// data/datasources/employee_remote_data_source.dart
import '../models/employee_model.dart';
import '../models/update_employee_payload.dart';

abstract class EmployeeRemoteDataSource {
  Future<EmployeeModel> getEmployee(String id);
  Future<List<EmployeeModel>> getEmployees({
    int page = 1,
    int limit = 20,
    String? departmentId,
  });
  Future<EmployeeModel> updateEmployee(
    String id,
    UpdateEmployeePayload payload,
  );
  Future<void> deleteEmployee(String id);
}
```

### Remote DataSource Implementation (Dio)

```dart
// data/datasources/employee_remote_data_source_impl.dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import '../models/base_response.dart';
import '../models/employee_model.dart';
import '../models/update_employee_payload.dart';
import 'employee_remote_data_source.dart';

@LazySingleton(as: EmployeeRemoteDataSource)
class EmployeeRemoteDataSourceImpl implements EmployeeRemoteDataSource {
  EmployeeRemoteDataSourceImpl({required this.dio});

  final Dio dio;

  @override
  Future<EmployeeModel> getEmployee(String id) async {
    final response = await dio.get('/api/v1/employees/$id');
    final base = BaseResponse<EmployeeModel>.fromJson(
      response.data as Map<String, dynamic>,
      fromJsonT: EmployeeModel.fromJson,
    );
    return base.data!;
  }

  @override
  Future<List<EmployeeModel>> getEmployees({
    int page = 1,
    int limit = 20,
    String? departmentId,
  }) async {
    final response = await dio.get(
      '/api/v1/employees',
      queryParameters: {
        'page': page,
        'limit': limit,
        if (departmentId != null) 'department_id': departmentId,
      },
    );
    final base = BaseResponse<List<dynamic>>.fromJson(
      response.data as Map<String, dynamic>,
      fromJsonT: (data) => data as List<dynamic>,
    );
    return (base.data ?? [])
        .map((e) => EmployeeModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<EmployeeModel> updateEmployee(
    String id,
    UpdateEmployeePayload payload,
  ) async {
    final response = await dio.put(
      '/api/v1/employees/$id',
      data: payload.toJson(),
    );
    final base = BaseResponse<EmployeeModel>.fromJson(
      response.data as Map<String, dynamic>,
      fromJsonT: EmployeeModel.fromJson,
    );
    return base.data!;
  }

  @override
  Future<void> deleteEmployee(String id) =>
      dio.delete('/api/v1/employees/$id');
}
```

### BaseResponse Wrapper

```dart
// data/models/base_response.dart
class BaseResponse<T> {
  const BaseResponse({
    this.status,
    this.message,
    this.data,
  });

  final int? status;
  final String? message;
  final T? data;

  factory BaseResponse.fromJson(
    Map<String, dynamic> json, {
    required T Function(dynamic) fromJsonT,
  }) =>
      BaseResponse<T>(
        status: json['status'] as int?,
        message: json['message'] as String?,
        data: json['data'] != null ? fromJsonT(json['data']) : null,
      );
}
```

---

## Repository Implementation <!-- 68 -->

Implement domain interfaces. Orchestrate datasource → mapper → Either.

```dart
// data/repositories/employee_repository_impl.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import '../../domain/entities/employee_entity.dart';
import '../../domain/errors/failure.dart';
import '../../domain/repositories/employee_repository.dart';
import '../../domain/usecases/employee/update_employee_usecase.dart';
import '../datasources/employee_remote_data_source.dart';
import '../exceptions/app_exception.dart';
import '../mappers/employee_mapper.dart';

@LazySingleton(as: EmployeeRepository)
class EmployeeRepositoryImpl implements EmployeeRepository {
  EmployeeRepositoryImpl({
    required this.remoteDataSource,
    required this.mapper,
  });

  final EmployeeRemoteDataSource remoteDataSource;
  final EmployeeMapper mapper;

  @override
  Future<Either<Failure, EmployeeEntity>> getEmployee(String id) async {
    try {
      final model = await remoteDataSource.getEmployee(id);
      return Right(mapper.toEntity(model));
    } on AppException catch (e) {
      return Left(e.toFailure());
    } catch (e) {
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, EmployeeEntity>> updateEmployee(
    String id,
    UpdateEmployeeParams params,
  ) async {
    try {
      final payload = UpdateEmployeePayload(
        name: params.name,
        email: params.email,
        departmentId: params.departmentId,
      );
      final model = await remoteDataSource.updateEmployee(id, payload);
      return Right(mapper.toEntity(model));
    } on AppException catch (e) {
      return Left(e.toFailure());
    } catch (e) {
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }
}
```

**Rules:**
- `try/catch` at the repository boundary — never in datasources
- Catch `AppException` first, then `catch (e)` for unexpected errors
- Null check `response.data` before mapping — log and return a failure if null
- Never let exceptions escape into the domain or presentation layers

---

## Exceptions <!-- 81 -->

Typed exceptions thrown by DataSources. Converted to `Failure` in repository.

```dart
// data/exceptions/app_exception.dart
import '../../domain/errors/failure.dart';

sealed class AppException implements Exception {
  const AppException(this.message);
  final String message;

  factory AppException.server({
    required String message,
    int? statusCode,
    String? errorCode,
  }) = ServerException;

  factory AppException.validation<T>({
    required String message,
    T? errors,
    int? statusCode,
  }) = ValidationException<T>;

  factory AppException.network({required String message}) =
      NetworkException;

  factory AppException.unknown({required String message}) =
      UnknownAppException;
}

final class ServerException extends AppException {
  const ServerException({
    required super.message,
    this.statusCode,
    this.errorCode,
  });
  final int? statusCode;
  final String? errorCode;
}

final class ValidationException<T> extends AppException {
  const ValidationException({
    required super.message,
    this.errors,
    this.statusCode,
  });
  final T? errors;
  final int? statusCode;
}

final class NetworkException extends AppException {
  const NetworkException({required super.message});
}

final class UnknownAppException extends AppException {
  const UnknownAppException({required super.message});
}

extension AppExceptionX on AppException {
  Failure toFailure() => switch (this) {
        ServerException e => Failure.serverFailure(
            message: e.message,
            developerMessage: 'HTTP ${e.statusCode}',
            statusCode: e.statusCode,
            errorCode: e.errorCode,
          ),
        ValidationException e => Failure.validationFailure(
            message: e.message,
            errors: e.errors,
            statusCode: e.statusCode,
          ),
        NetworkException e => Failure.networkFailure(message: e.message),
        UnknownAppException e =>
          Failure.unknownFailure(message: e.message),
      };
}
```

---

## HTTP Client <!-- 44 -->

Translate Dio errors → `AppException` before they reach the repository.

```dart
// data/network/error_interceptor.dart
import 'package:dio/dio.dart';
import '../exceptions/app_exception.dart';

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
        (err.response?.data as Map<String, dynamic>?)?['message']
            as String? ??
        err.message ??
        'Server error';
    return statusCode == 422
        ? AppException.validation(message: message, statusCode: statusCode)
        : AppException.server(
            message: message,
            statusCode: statusCode,
          );
  }
}
```

---

## Endpoint Constants <!-- 19 -->

```dart
// data/network/endpoints.dart
abstract class Endpoints {
  Endpoints._();

  static const String _v1 = '/api/v1';

  static const String employees = '$_v1/employees';
  static String employee(String id) => '$employees/$id';

  static const String attendance = '$_v1/attendance';
  static String clockIn = '$attendance/clock-in';
}
```

---

## Local Data Source (Cache-First Pattern) <!-- 33 -->

```dart
// data/datasources/employee_local_data_source.dart
abstract class EmployeeLocalDataSource {
  Future<EmployeeModel?> getCachedEmployee(String id);
  Future<void> cacheEmployee(String id, EmployeeModel model);
  Future<void> clearCache();
}
```

```dart
// data/repositories/employee_repository_impl.dart (cache-first variant)
@override
Future<Either<Failure, EmployeeEntity>> getEmployee(String id) async {
  // 1. Try cache
  final cached = await localDataSource.getCachedEmployee(id);
  if (cached != null) {
    return Right(mapper.toEntity(cached));
  }

  // 2. Fetch remote
  try {
    final model = await remoteDataSource.getEmployee(id);
    await localDataSource.cacheEmployee(id, model);
    return Right(mapper.toEntity(model));
  } on AppException catch (e) {
    return Left(e.toFailure());
  } catch (e) {
    return Left(Failure.unknownFailure(message: e.toString()));
  }
}
```
