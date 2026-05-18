---
name: builder-data-create-datasource
description: Create a RemoteDataSource abstract class and its Dio-based implementation for a Flutter Qontak feature. Throws AppException, never returns Either.
user-invocable: false
---

Create a DataSource following `lib/platforms/flutter-qontak/reference/code-architecture/data-impl.md ## Data Sources section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/data-impl.md` for `## Data Sources`; only **Read** the full file if the section cannot be located
2. **Verify** the DTO model exists — run `builder-data-create-mapper` first if missing
3. **Check** if a Request body is needed for write operations — create `[concept]_request.dart` under `data/models/` if so
4. **Locate** path: `features/[prefix]_[feature]/lib/src/data/datasources/`
5. **Create** `[feature]_remote_data_source.dart` — abstract interface and implementation in the same file

## DataSource Pattern

```dart
// features/[prefix]_[feature]/lib/src/data/datasources/[feature]_remote_data_source.dart
import 'package:dio/dio.dart';
import '../models/[concept]_response.dart';
import '../models/[concept]_request.dart'; // only if write operations exist

abstract class [Feature]RemoteDataSource {
  // throws AppException — never returns Either
  Future<[Concept]Response> get[Concept](String id);
  Future<List<[Concept]Response>> get[Concept]s();
  Future<[Concept]Response> update[Concept](String id, [Concept]Request request);
  Future<void> delete[Concept](String id);
}

// No @LazySingleton — registration is manual in [Feature]Dependency._registerData()
class [Feature]RemoteDataSourceImpl implements [Feature]RemoteDataSource {
  [Feature]RemoteDataSourceImpl({required this.dio});
  final Dio dio;

  @override
  Future<[Concept]Response> get[Concept](String id) async {
    final response = await dio.get('/api/v1/[feature]/$id');
    return [Concept]Response.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<List<[Concept]Response>> get[Concept]s() async {
    final response = await dio.get('/api/v1/[feature]');
    final list = response.data as List<dynamic>;
    return list
        .map((e) => [Concept]Response.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<[Concept]Response> update[Concept](String id, [Concept]Request request) async {
    final response = await dio.put(
      '/api/v1/[feature]/$id',
      data: request.toJson(),
    );
    return [Concept]Response.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<void> delete[Concept](String id) => dio.delete('/api/v1/[feature]/$id');
}
```

## DI Registration (caller adds to [Feature]Dependency)

```dart
// In [Feature]Dependency._registerData():
[feature]Dependency.registerLazySingleton<[Feature]RemoteDataSource>(
  () => [Feature]RemoteDataSourceImpl(dio: coreDependency()),
);
```

## Rules

- Abstract interface + implementation in the same file (cohesive unit)
- Throws `AppException` — never returns `Either` (the repository catches it)
- `Dio` injected via constructor — never created inside the datasource
- No `@LazySingleton` annotation — registration is manual in the feature package's DI class
- No BLoC or domain imports

## Output

Confirm file path and list all declared method signatures.
