---
name: builder-data-create-datasource
description: Create a RemoteDataSource abstract class and its Dio-based implementation for a feature.
user-invocable: false
---

Create a DataSource following `.claude/reference/code-architecture/data-impl.md ## Data Sources section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/data-impl.md` for `## Data Sources`; only **Read** the full file if the section cannot be located
2. **Verify** the Model exists — run `data-create-mapper` first if missing
3. **Check** if a Payload is needed for write operations — create it under `data/models/` if so
4. **Locate** path: `lib/src/features/[feature]/data/datasources/`
5. **Create** `[feature]_remote_data_source.dart` (abstract) and `[feature]_remote_data_source_impl.dart`

## DataSource Abstract Pattern

```dart
import '../models/[feature]_model.dart';

abstract class [Feature]RemoteDataSource { // no annotations — throws AppException, never returns Either
  Future<[Feature]Model> get[Feature](String id);
  Future<List<[Feature]Model>> get[Feature]s({int page = 1, int limit = 20});
  Future<[Feature]Model> update[Feature](String id, Update[Feature]Payload payload);
  Future<void> delete[Feature](String id);
}
```

## DataSource Impl Pattern

```dart
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import '../models/base_response.dart';
import '../models/[feature]_model.dart';
import '../models/update_[feature]_payload.dart';
import '../exceptions/app_exception.dart';
import '[feature]_remote_data_source.dart';

@LazySingleton(as: [Feature]RemoteDataSource) // inject Dio — never create Dio() inside
class [Feature]RemoteDataSourceImpl implements [Feature]RemoteDataSource {
  [Feature]RemoteDataSourceImpl({required this.dio});

  final Dio dio;

  @override
  Future<[Feature]Model> get[Feature](String id) async {
    final response = await dio.get('/api/v1/[features]/$id');
    final base = BaseResponse<[Feature]Model>.fromJson(
      response.data as Map<String, dynamic>,
      fromJsonT: [Feature]Model.fromJson,
    );
    return base.data!;
  }
}
```

## Output

Confirm both file paths and list all declared method signatures.
