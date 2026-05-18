---
name: flutter-qontak-crm-build-feature
description: Add a new feature module to the Qontak CRM monorepo following the crm_* package structure with Clean Architecture layers.
user-invocable: false
---

## Steps

### 1 — Create the feature package directory

Create `features/<crm_or_qontak>_<domain>/` at the repo root. Use `crm_` prefix for CRM-domain features and `qontak_` for cross-product features.

```
features/crm_<domain>/
├── pubspec.yaml
├── analysis_options.yaml
├── lib/
│   ├── crm_<domain>.dart        ← public barrel export
│   └── src/
│       ├── crm_<domain>.dart    ← BaseModule class
│       ├── config/
│       ├── data/
│       ├── domain/
│       └── presentation/
```

### 2 — Write pubspec.yaml

Copy the pattern from `features/crm_company/pubspec.yaml`. Minimum required dependencies:
- `crm_core` (git path dep pointing to `features/crm_core`)
- `flutter` SDK
- `flutter_localizations` SDK + `intl: 0.19.0`

Dev dependencies: `build_runner`, `freezed`, `json_serializable`, `isar_generator` or `objectbox_generator`, `flutter_lints`, `bloc_test`, `mockito`, `http_mock_adapter`.

Set `flutter: generate: true`.

### 3 — Write analysis_options.yaml

```yaml
include: linter-rules/analysis_options_mekari.yml
analyzer:
  errors:
    invalid_annotation_target: ignore
```

### 4 — Create the BaseModule class

In `lib/src/crm_<domain>.dart`:

```dart
import 'package:crm_core/crm_dependency.dart';
import 'package:crm_core/qontak_common.dart';
import 'package:flutter/material.dart';

export 'config/config.dart';
export 'data/data.dart';
export 'domain/domain.dart';
export 'presentation/presentation.dart';

class CRM<Domain>Module implements BaseModule {
  @override
  LocalizationsDelegate? localizationsDelegate() {
    if (FlavorChecker.isPyridam) {
      return Pyridam<Domain>Localizations.delegate;
    } else if (FlavorChecker.isKrasSalesGo) {
      return KRAS<Domain>Localizations.delegate;
    } else {
      return CRM<Domain>Localizations.delegate;
    }
  }

  @override
  List<CollectionSchema> collectionSchemas() => [
        <Domain>DBSchema,
      ];
}
```

If no Isar schemas exist yet, return an empty list.

### 5 — Create the domain layer

**Entity** (`lib/src/domain/entities/<name>/<name>.dart`):
```dart
import 'package:crm_core/crm_dependency.dart';

part '<name>.freezed.dart';

@freezed
class <Name> with _$<Name> {
  const factory <Name>({
    required String id,
    // ... fields
  }) = _<Name>;
  const <Name>._();
}
```

**Repository interface** (`lib/src/domain/repositories/<name>_repository.dart`):
```dart
import 'package:crm_core/crm_dependency.dart' hide Failure;
import 'package:crm_core/qontak_common.dart';

abstract class <Name>Repository {
  Future<Either<Failure, <Name>>> get<Name>ById({required String id});
  // ... other methods
}
```

**Use cases** (`lib/src/domain/usecases/<verb>_<name>_usecase.dart`):
```dart
import 'package:crm_core/crm_dependency.dart' hide Failure;
import 'package:crm_core/qontak_common.dart';

class Get<Name>ByIdUseCase extends UseCase<<Name>, String> {
  Get<Name>ByIdUseCase({required this.repository});
  final <Name>Repository repository;

  @override
  Future<Either<Failure, <Name>>> call(String params) =>
      repository.get<Name>ById(id: params);
}
```

### 6 — Create the data layer

**Remote model** (`lib/src/data/models/remote/<name>_response/<name>_response.dart`):
```dart
import 'package:crm_core/crm_dependency.dart';

part '<name>_response.freezed.dart';
part '<name>_response.g.dart';

@freezed
class <Name>Response with _$<Name>Response {
  const factory <Name>Response({
    @JsonKey(name: 'id') required String id,
    // ... fields
  }) = _<Name>Response;

  factory <Name>Response.fromJson(Map<String, dynamic> json) =>
      _$<Name>ResponseFromJson(json);
}
```

**Remote data source** (`lib/src/data/data_sources/remote/<name>_remote_data_source.dart`):
```dart
import 'package:crm_core/qontak_common.dart' hide Endpoint;
import 'package:crm_<domain>/src/config/constants/endpoint.dart';
import 'package:crm_<domain>/src/data/models/remote/<name>_response/<name>_response.dart';

abstract class <Name>RemoteDataSource {
  Future<BaseResponse<<Name>Response>> get<Name>ById({required String id});
}

class <Name>RemoteDataSourceImpl implements <Name>RemoteDataSource {
  const <Name>RemoteDataSourceImpl({required this.baseApi});
  final BaseApi baseApi;

  @override
  Future<BaseResponse<<Name>Response>> get<Name>ById({required String id}) async {
    final response = await baseApi.get(Endpoint.<name>ById(id: id));
    return BaseResponse<<Name>Response>.fromJson(
      response,
      onDeserializedT: (r) => <Name>Response.fromJson(r),
    );
  }
}
```

**Repository impl** (`lib/src/data/repositories/<name>_repository_impl.dart`):
Implement the domain interface. Use `TaskEither.tryCatch(...)` for error wrapping. Map responses to entities via a mapper class.

**Mapper** (`lib/src/data/mappers/<name>_mapper.dart`):
```dart
class <Name>Mapper {
  static <Name> fromResponseToEntity({required <Name>Response? source}) =>
      <Name>(id: source?.id ?? '', /* ... */);
}
```

### 7 — Create the DI class

`lib/src/config/di/qontak_<domain>_dependency.dart`:
```dart
import 'package:crm_core/crm_dependency.dart';
import 'package:crm_core/qontak_common.dart';

final qontak<Domain>Dependency = GetIt.instance;

class Qontak<Domain>Dependency {
  static void register<Domain>() {
    _register<Domain>Data();
    _register<Domain>Domain();
  }

  static void _register<Domain>Data() {
    qontak<Domain>Dependency
      ..registerLazySingleton<<Name>RemoteDataSource>(
        () => <Name>RemoteDataSourceImpl(baseApi: qontakCommonDependency()),
      )
      ..registerLazySingleton<<Name>Repository>(
        () => <Name>RepositoryImpl(remoteDataSource: qontak<Domain>Dependency()),
      );
  }

  static void _register<Domain>Domain() {
    qontak<Domain>Dependency.registerLazySingleton<Get<Name>ByIdUseCase>(
      () => Get<Name>ByIdUseCase(repository: qontak<Domain>Dependency()),
    );
  }
}
```

### 8 — Register the feature in the app

In `lib/configs/di/crm_di.dart`, add:
```dart
Qontak<Domain>Dependency.register<Domain>();
```

In `lib/configs/modules.dart`, add `CRM<Domain>Module()` to `featureModules`.

In `pubspec.yaml` (root), add the new feature as a git-path dependency following the existing pattern.

### 9 — Create barrel exports

Each layer folder needs a barrel file (e.g. `config/config.dart`, `data/data.dart`, `domain/domain.dart`, `presentation/presentation.dart`) that exports all sub-files.

### 10 — Run code generation

```bash
cd features/crm_<domain>
dart run build_runner build --delete-conflicting-outputs
```
