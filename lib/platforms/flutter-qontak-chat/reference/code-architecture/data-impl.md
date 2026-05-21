# Flutter Qontak — Data Layer

> Concepts and invariants: `lib/core/reference/code-architecture/data-theory.md`. This file covers Dart syntax and patterns.

Data lives inside each feature package at `lib/src/data/`. It implements domain interfaces and handles serialization, HTTP, and local storage.

---

## Dependency Rule <!-- 13 -->

Data depends on Domain only. It never imports from Presentation or UI.

**Allowed:** `package:dio`, `package:hive`, `package:shared_preferences`, `package:injectable`, `package:freezed_annotation`, domain entities and repository interfaces from `package:[prefix]_core` or sibling feature packages (via their public API only).

**Forbidden:**

- Any BLoC or Cubit import (`package:flutter_bloc`, `package:bloc`)
- `package:flutter/material.dart` or any UI package
- Any presentation-layer type — data must not know how results are displayed

---

## DTO Models <!-- 68 -->

Three kinds of DTO — all nullable fields, all with `fromJson`.

### API Response Model (`*Response`)

```dart
// [prefix]_auth/lib/src/data/models/login_response.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'login_response.freezed.dart';
part 'login_response.g.dart';

@freezed
class LoginResponse with _$LoginResponse {
  const factory LoginResponse({
    @JsonKey(name: 'access_token') String? accessToken,
    @JsonKey(name: 'refresh_token') String? refreshToken,
    @JsonKey(name: 'expires_in') int? expiresIn,
    UserResponse? user,
  }) = _LoginResponse;

  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);
}
```

### API Request Body (`*Request`)

```dart
// [prefix]_auth/lib/src/data/models/login_request.dart
@freezed
class LoginRequest with _$LoginRequest {
  const factory LoginRequest({
    required String email,
    required String password,
  }) = _LoginRequest;

  factory LoginRequest.fromJson(Map<String, dynamic> json) =>
      _$LoginRequestFromJson(json);
}
```

### Database Entity (`*Db`)

```dart
// [prefix]_auth/lib/src/data/models/user_db.dart
@freezed
class UserDb with _$UserDb {
  const factory UserDb({
    String? id,
    String? name,
    String? email,
    String? cachedAt,
  }) = _UserDb;

  factory UserDb.fromJson(Map<String, dynamic> json) =>
      _$UserDbFromJson(json);
}
```

**Rules:**

- All fields nullable — API data is untrusted; handle defaults in mapper
- `@JsonKey(name:)` for snake_case ↔ camelCase mapping
- No business logic in models

---

## Mappers <!-- 43 -->

Static class with explicit `from{Source}To{Destination}` naming:

```dart
// [prefix]_auth/lib/src/data/mappers/user_mapper.dart
import '../../domain/entities/user.dart';
import '../models/user_response.dart';
import '../models/user_db.dart';

class UserMapper {
  const UserMapper._();

  static User fromResponseToEntity(UserResponse r) => User(
        id: r.id ?? '',
        name: r.name ?? '',
        email: r.email ?? '',
        joinDate: r.joinDate != null ? DateTime.tryParse(r.joinDate!) : null,
      );

  static UserDb fromEntityToDb(User u) => UserDb(
        id: u.id,
        name: u.name,
        email: u.email,
        cachedAt: DateTime.now().toIso8601String(),
      );

  static User fromDbToEntity(UserDb db) => User(
        id: db.id ?? '',
        name: db.name ?? '',
        email: db.email ?? '',
      );
}
```

**Rules:**

- Private constructor `._()` to prevent instantiation (no mocking needed — pure functions)
- One mapper class per domain entity
- Handle nulls with explicit defaults — never assume API fields are present
- Date string → `DateTime` conversion happens in mapper, not entity

---

## Data Sources <!-- 45 -->

Abstract interface + implementation in same file (cohesive unit).

```dart
// [prefix]_auth/lib/src/data/datasources/auth_remote_data_source.dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import '../models/login_request.dart';
import '../models/login_response.dart';
import '../models/user_response.dart';

abstract class AuthRemoteDataSource {
  Future<LoginResponse> login(LoginRequest request);
  Future<UserResponse> getCurrentUser();
  Future<void> logout();
}

@LazySingleton(as: AuthRemoteDataSource)
class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  AuthRemoteDataSourceImpl(this._dio);
  final Dio _dio;

  @override
  Future<LoginResponse> login(LoginRequest request) async {
    final response = await _dio.post(
      '/api/v1/auth/login',
      data: request.toJson(),
    );
    return LoginResponse.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<UserResponse> getCurrentUser() async {
    final response = await _dio.get('/api/v1/auth/me');
    return UserResponse.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<void> logout() => _dio.post('/api/v1/auth/logout');
}
```

---

## Multi-Source Mapping Pattern <!-- 42 -->

Apply when a single domain entity is assembled from two or more distinct data sources (e.g. two REST APIs, or REST + local DB).

**Rule:** The Repository Implementation is the only layer that sees multiple sources. It merges results and hands the mapper a single, complete data object. Mappers receive one input type; they never fan-out to other sources.

**Structure:**

1. Declare one `Mapper` per source.
2. In the Repository, call both sources, then apply a `merge` or composite-map step.
3. The entity produced is identical whether one source or both are available — absent data fills in domain defaults.

```dart
// [prefix]_chat/lib/src/data/repositories/message_repository_impl.dart
@LazySingleton(as: MessageRepository)
class MessageRepositoryImpl implements MessageRepository {
  final MessageRemoteDataSource _remoteSource;
  final MessageLocalDataSource _localSource;
  final MessageRemoteMapper _remoteMapper;
  final MessageLocalMapper _localMapper;

  MessageRepositoryImpl(
    this._remoteSource,
    this._localSource,
    this._remoteMapper,
    this._localMapper,
  );

  @override
  TaskEither<Failure, Message> getMessage(String id) =>
      TaskEither.tryCatch(
        () async {
          final remoteDto = await _remoteSource.getMessage(id);
          final localDto = await _localSource.getMessage(id).getOrNull(); // nullable
          return _remoteMapper.toDomain(remoteDto, localOverlay: localDto != null ? _localMapper.toOverlay(localDto) : null);
        },
        (e, _) => mapException(e),
      );
}
```

**Vocabulary rule:** The merged entity uses one canonical term for each concept. Both mappers translate to the canonical term — no API-originated names survive into the domain.

**DI (Chat `@injectable`):** Annotate the `RepositoryImpl` with `@LazySingleton(as: MessageRepository)`. The `@injectable` code generator wires all constructor dependencies automatically.

---

## Repository Implementation <!-- 63 -->

```dart
// [prefix]_auth/lib/src/data/repositories/auth_repository_impl.dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:[prefix]_core/[prefix]_core.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_data_source.dart';
import '../exceptions/app_exception.dart';
import '../mappers/user_mapper.dart';

@LazySingleton(as: AuthRepository)
class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl(this._remoteDataSource);
  final AuthRemoteDataSource _remoteDataSource;

  @override
  Future<Either<Failure, User>> login(String email, String password) async {
    try {
      final response = await _remoteDataSource.login(
        LoginRequest(email: email, password: password),
      );
      if (response.user == null) {
        return Left(Failure.unknownFailure(message: 'User not returned'));
      }
      return Right(UserMapper.fromResponseToEntity(response.user!));
    } on AppException catch (e) {
      return Left(e.toFailure());
    } catch (e) {
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, User>> getCurrentUser() async {
    try {
      final response = await _remoteDataSource.getCurrentUser();
      return Right(UserMapper.fromResponseToEntity(response));
    } on AppException catch (e) {
      return Left(e.toFailure());
    } catch (e) {
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> logout() async {
    try {
      await _remoteDataSource.logout();
      return const Right(null);
    } on AppException catch (e) {
      return Left(e.toFailure());
    } catch (e) {
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }
}
```

---

## Endpoint Constants <!-- 16 -->

```dart
// [prefix]_auth/lib/src/data/network/auth_endpoints.dart
abstract class AuthEndpoints {
  AuthEndpoints._();
  static const String _base = '/api/v1/auth';
  static const String login = '$_base/login';
  static const String me = '$_base/me';
  static const String logout = '$_base/logout';
  static const String refresh = '$_base/refresh';
}
```

---

## AppException (shared in `[prefix]_core`) <!-- 46 -->

```dart
// shared/[prefix]_core/lib/src/data/app_exception.dart
sealed class AppException implements Exception {
  const AppException(this.message);
  final String message;

  factory AppException.server({required String message, int? statusCode, String? errorCode}) = ServerException;
  factory AppException.validation<T>({required String message, T? errors, int? statusCode}) = ValidationException<T>;
  factory AppException.network({required String message}) = NetworkException;
  factory AppException.unknown({required String message}) = UnknownAppException;
}

final class ServerException extends AppException {
  const ServerException({required super.message, this.statusCode, this.errorCode});
  final int? statusCode;
  final String? errorCode;
}
final class ValidationException<T> extends AppException {
  const ValidationException({required super.message, this.errors, this.statusCode});
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
    ValidationException e => Failure.validationFailure(message: e.message, errors: e.errors, statusCode: e.statusCode),
    NetworkException e => Failure.networkFailure(message: e.message),
    UnknownAppException e => Failure.unknownFailure(message: e.message),
  };
}
```

## Creation Order <!-- 21 -->

When building a new feature's data layer, create files in this sequence:

```
1. [prefix]_[feature]/lib/src/data/models/[concept]_response.dart
                                                     ← API response DTO (@freezed, fromJson, .g.dart)
   [prefix]_[feature]/lib/src/data/models/[concept]_request.dart
                                                     ← API request body (if POST/PUT)
   [prefix]_[feature]/lib/src/data/models/[concept]_db.dart
                                                     ← DB record (if local persistence needed)
2. [prefix]_[feature]/lib/src/data/mappers/[concept]_mapper.dart
                                                     ← Mapper (static class, from{Source}To{Dest})
3. [prefix]_[feature]/lib/src/data/datasources/[feature]_remote_data_source.dart
                                                     ← DataSource abstract class + implementation
4. [prefix]_[feature]/lib/src/data/repositories/[feature]_repository_impl.dart
                                                     ← Repository implementation
```

Never create a repository implementation before the data source it depends on.

## Layer Invariants <!-- 7 -->

- Import from domain layer only — never from presentation, BLoC, Cubit, or widget files
- `AppException` subtypes thrown by DataSources are caught and converted to `Failure` in the repository `try/catch` boundary — never propagated to domain or presentation
- `*Response`, `*Request`, and `*Db` model instances never cross into the domain layer — `[Concept]Mapper.from*To*()` is the boundary
- Repository implementation is registered with `@LazySingleton(as: RepositoryInterface)` — the concrete class is never referenced outside the data layer
- `Dio` and Hive boxes live only in DataSource implementations — never in repository or domain files
