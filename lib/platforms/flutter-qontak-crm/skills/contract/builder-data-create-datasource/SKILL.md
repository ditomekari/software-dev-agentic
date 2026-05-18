---
name: builder-data-create-datasource
description: Create a RemoteDataSource abstract class and its BaseApi-based implementation for a Flutter Qontak CRM feature. Throws exceptions, never returns Either.
user-invocable: false
---

Create a DataSource following `lib/platforms/flutter-qontak-crm/reference/code-architecture/data-impl.md ## Data Sources`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak-crm/reference/code-architecture/data-impl.md` for `## Data Sources`; only **Read** the full file if the section cannot be located
2. **Verify** the DTO model exists — run `builder-data-create-mapper` first if missing
3. **Check** if a Request body is needed for write operations — create `[concept]_request.dart` under `data/models/remote/` if so
4. **Locate** path: `features/[prefix]_[feature]/lib/src/data/data_sources/remote/`
5. **Create** `[feature]_remote_data_source.dart` — abstract interface and implementation in the same file

## DataSource Pattern

```dart
// features/[prefix]_[feature]/lib/src/data/data_sources/remote/[feature]_remote_data_source.dart
import 'package:mekari_network/mekari_network.dart'; // re-exports BaseApi
import '../models/remote/[concept]_response.dart';
import '../models/remote/[concept]_request.dart'; // only if write operations exist

abstract class [Feature]RemoteDataSource {
  // throws exception — never returns Either
  Future<[Concept]Response> get[Concept](String id);
  Future<List<[Concept]Response>> get[Concept]List();
  Future<[Concept]Response> update[Concept](String id, [Concept]Request request);
  Future<void> delete[Concept](String id);
}

// No @LazySingleton — registration is manual in Qontak[Feature]Dependency
class [Feature]RemoteDataSourceImpl implements [Feature]RemoteDataSource {
  [Feature]RemoteDataSourceImpl({required this.baseApi});
  final BaseApi baseApi;

  @override
  Future<[Concept]Response> get[Concept](String id) async {
    final response = await baseApi.get(Endpoint.[concept](id));
    return [Concept]Response.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<List<[Concept]Response>> get[Concept]List() async {
    final response = await baseApi.get(Endpoint.[concept]List);
    final list = response.data as List<dynamic>;
    return list
        .map((e) => [Concept]Response.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<[Concept]Response> update[Concept](String id, [Concept]Request request) async {
    final response = await baseApi.put(
      Endpoint.[concept](id),
      data: request.toJson(),
    );
    return [Concept]Response.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<void> delete[Concept](String id) => baseApi.delete(Endpoint.[concept](id));
}
```

## DI Registration (caller adds to Qontak[Feature]Dependency)

```dart
// In Qontak[Feature]Dependency._register[Feature]Data():
qontak[Feature]Dependency.registerLazySingleton<[Feature]RemoteDataSource>(
  () => [Feature]RemoteDataSourceImpl(baseApi: qontakCommonDependency()),
);
```

## Rules

- Abstract interface + implementation in the same file (cohesive unit)
- Throws exception — never returns `Either` (the repository catches it)
- `BaseApi` (from `mekari_network`) injected via constructor — never created inside the datasource
- No `@LazySingleton` annotation — registration is manual in the feature's `Qontak<Feature>Dependency` class
- No BLoC or domain imports
- Endpoint constants come from `lib/src/config/constants/endpoint.dart` in the feature package

## Output

Confirm file path and list all declared method signatures.
