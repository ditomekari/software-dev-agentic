# Flutter Qontak CRM — Data Layer

> Concepts and invariants: `lib/core/reference/code-architecture/data-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

Data lives inside each feature package at `features/<pkg>/lib/src/data/`. It implements domain interfaces and handles serialization, HTTP, and local storage (Isar / ObjectBox).

---

## Dependency Rule <!-- 13 -->

Data depends on Domain only. It never imports from Presentation or UI.

**Allowed:** `package:mekari_network` (re-exports `BaseApi`), `package:fpdart`, `package:freezed_annotation`, `package:qontak_common`, domain entities and repository interfaces from the same feature package.

**Forbidden:**
- Any BLoC or Cubit import (`package:flutter_bloc`, `package:bloc`)
- `package:flutter/material.dart` or any UI package
- Any presentation-layer type

---

## DTO Models <!-- 78 -->

Three kinds of DTO — all nullable fields, all with `fromJson`.

### API Response Model (`*Response`) — feature packages

```dart
// features/crm_company/lib/src/data/models/remote/company_response.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'company_response.freezed.dart';
part 'company_response.g.dart';

@freezed
class CompanyResponse with _$CompanyResponse {
  const factory CompanyResponse({
    @JsonKey(name: 'id') String? id,
    @JsonKey(name: 'name') String? name,
    @JsonKey(name: 'phone') String? phone,
    @JsonKey(name: 'created_at') String? createdAt,
  }) = _CompanyResponse;

  factory CompanyResponse.fromJson(Map<String, dynamic> json) =>
      _$CompanyResponseFromJson(json);
}
```

Note: feature packages use `Response`/`Request` suffix; app-root models (`lib/data/`) use `Model` suffix.

### API Request Body (`*Request`)

```dart
@freezed
class CompanyFilterRequest with _$CompanyFilterRequest {
  const factory CompanyFilterRequest({
    @JsonKey(name: 'search') String? search,
    @JsonKey(name: 'page') int? page,
  }) = _CompanyFilterRequest;

  factory CompanyFilterRequest.fromJson(Map<String, dynamic> json) =>
      _$CompanyFilterRequestFromJson(json);
}
```

### Isar DB Model (`*Db`)

```dart
// Isar collection model (legacy — prefer ObjectBox for new code)
@Collection()
class CompanyDb {
  Id id = Isar.autoIncrement;
  String? remoteId;
  String? name;
  String? createdAt;
}
```

### ObjectBox Model (`*ObjectBox`)

```dart
@Entity()
class CompanyObjectBox {
  @Id()
  int id = 0;
  String? remoteId;
  String? name;
  String? createdAt;
}
```

**Rules:**
- All fields nullable — API data is untrusted; handle defaults in mapper
- `@JsonKey(name:)` for snake_case ↔ camelCase mapping
- Both `.freezed.dart` and `.g.dart` parts required on DTOs (unlike entities which have only `.freezed.dart`)
- No business logic in models

---

## Mappers <!-- 41 -->

Static-only classes. Naming: `<Feature>Mapper`, with methods named `from{Source}To{Target}`.

```dart
// features/crm_company/lib/src/data/mappers/company_mapper.dart
import '../../domain/entities/company.dart';
import '../models/remote/company_response.dart';
import '../models/local/company_db.dart';

class CompanyMapper {
  const CompanyMapper._(); // private constructor — pure static functions

  static Company fromResponseToEntity(CompanyResponse r) => Company(
        id: r.id ?? '',
        name: r.name ?? '',
        phone: r.phone,
        createdAt: r.createdAt != null ? DateTime.tryParse(r.createdAt!) : null,
      );

  static CompanyDb fromEntityToDb(Company c) => CompanyDb()
    ..remoteId = c.id
    ..name = c.name
    ..createdAt = c.createdAt?.toIso8601String();

  static Company fromDbToEntity(CompanyDb db) => Company(
        id: db.remoteId ?? '',
        name: db.name ?? '',
      );
}
```

**Rules:**
- Private constructor `._()` to prevent instantiation
- One mapper class per domain entity (may have multiple static methods)
- Handle nulls with explicit defaults — never assume API fields are present
- Date string → `DateTime` conversion in mapper, not entity
- App-root mappers: `CrmMapper<Source>To<Target>` (e.g. `CrmMapperModelToEntity`)

---

## Data Sources <!-- 47 -->

Abstract interface + implementation in the same file. Remote sources take `BaseApi`; local sources take `DatabaseService.instance` or an ObjectBox adapter.

```dart
// features/crm_company/lib/src/data/data_sources/remote/company_remote_data_source.dart
import 'package:mekari_network/mekari_network.dart'; // re-exports BaseApi

abstract class CompanyRemoteDataSource {
  // throws exception — never returns Either
  Future<CompanyResponse> getCompany(String id);
  Future<List<CompanyResponse>> getCompanyList();
  Future<CompanyResponse> addCompany(CompanyFilterRequest request);
  Future<void> deleteCompany(String id);
}

// No @LazySingleton — registration is manual in QontakCompanyDependency
class CompanyRemoteDataSourceImpl implements CompanyRemoteDataSource {
  CompanyRemoteDataSourceImpl({required this.baseApi});
  final BaseApi baseApi;

  @override
  Future<CompanyResponse> getCompany(String id) async {
    final response = await baseApi.get(Endpoint.company(id));
    return CompanyResponse.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<List<CompanyResponse>> getCompanyList() async {
    final response = await baseApi.get(Endpoint.companyList);
    final list = response.data as List<dynamic>;
    return list.map((e) => CompanyResponse.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<CompanyResponse> addCompany(CompanyFilterRequest request) async {
    final response = await baseApi.post(Endpoint.companyList, data: request.toJson());
    return CompanyResponse.fromJson(response.data as Map<String, dynamic>);
  }

  @override
  Future<void> deleteCompany(String id) => baseApi.delete(Endpoint.company(id));
}
```

---

## Multi-Source Mapping Pattern <!-- 42 -->

Apply when a single domain entity is assembled from two or more distinct data sources (e.g. CRM API + CDP API, or REST + local DB).

**Rule:** The Repository Implementation is the only layer that sees multiple sources. It merges results and hands the mapper a single, complete data object. Mappers receive one input type; they never fan-out to other sources.

**Structure:**
1. Declare one `Mapper` per source.
2. In the Repository, call both sources, then apply a `merge` or composite-map step.
3. The entity produced is identical whether one source or both are available — absent data fills in domain defaults.

```dart
// features/crm_contact/lib/src/data/repositories/contact_repository_impl.dart
class ContactRepositoryImpl implements ContactRepository {
  final CrmContactRemoteDataSource _crmSource;
  final CdpContactRemoteDataSource _cdpSource;
  final CrmContactMapper _crmMapper;
  final CdpContactMapper _cdpMapper;

  ContactRepositoryImpl(
    this._crmSource,
    this._cdpSource,
    this._crmMapper,
    this._cdpMapper,
  );

  @override
  TaskEither<Failure, Contact> getContact(String id) =>
      TaskEither.tryCatch(
        () async {
          final crmDto = await _crmSource.getContact(id);
          final cdpDto = await _cdpSource.getContact(id).getOrNull(); // nullable — CDP may not have it
          // Merge into a single, type-safe record before mapping
          return _crmMapper.toDomain(crmDto, cdpOverlay: cdpDto != null ? _cdpMapper.toOverlay(cdpDto) : null);
        },
        (e, _) => mapException(e),
      );
}
```

**Vocabulary rule:** The merged entity uses one canonical term for each concept. If CRM calls it `person` and CDP calls it `contact`, pick one. Both mappers translate to the canonical term — no API-originated names survive into the domain.

**DI (CRM manual GetIt):** Both `DataSource` instances and both `Mapper` instances are passed through `QontakXxxDependency` and injected into the `RepositoryImpl` constructor.

---

## Repository Implementation <!-- 41 -->

Two acceptable patterns — `TaskEither.tryCatch` (FP style, used in newer packages) or manual `try/catch`. Be consistent within a feature.

```dart
// features/crm_company/lib/src/data/repositories/company_repository_impl.dart
import 'package:fpdart/fpdart.dart';
import 'package:qontak_common/qontak_common.dart'; // Failure, QontakMonitor

// No @LazySingleton — registration is manual in QontakCompanyDependency
class CompanyRepositoryImpl implements CompanyRepository {
  CompanyRepositoryImpl({required this.remoteDataSource});
  final CompanyRemoteDataSource remoteDataSource;

  @override
  Future<Either<Failure, Company>> getCompany(String id) async {
    try {
      final response = await remoteDataSource.getCompany(id);
      return Right(CompanyMapper.fromResponseToEntity(response));
    } on Exception catch (e, _) {
      qontakCommonDependency<QontakMonitor>().logCrashMonitor(
        logName: CompanyLogConstant.getCompany,
      );
      return Left(Failure(message: e.toString()));
    }
  }
}
```

**TaskEither variant (FP style):**
```dart
@override
Future<Either<Failure, Company>> getCompany(String id) =>
    TaskEither.tryCatch(
      () => remoteDataSource.getCompany(id),
      (error, _) => Failure(message: error.toString()),
    ).map(CompanyMapper.fromResponseToEntity).run();
```

---

## Dual-DB Migration <!-- 23 -->

The app is migrating from Isar to ObjectBox. `DataSourceSwapHelper.shouldUseObjectBox` determines the active backend.

```dart
class CompanyDataLocalDataSourceImpl implements CompanyDataLocalDataSource {
  @override
  Future<List<Company>> getLocalCompanies() async {
    if (DataSourceSwapHelper.shouldUseObjectBox) {
      return _getFromObjectBox();
    }
    return _getFromIsar();
  }
}
```

**Rules:**
- Features already in migration must implement both paths
- New features: use ObjectBox only — Isar is legacy
- `DataSourceSwapHelper.shouldUseObjectBox` is the single switch point per data source

---

## DI Registration Pattern <!-- 34 -->

```dart
// features/crm_company/lib/src/config/di/qontak_company_dependency.dart
final qontakCompanyDependency = GetIt.instance;

class QontakCompanyDependency {
  static void registerCompany() {
    _registerDatabase();
    _registerObjectBox();
    _registerCompanyData();
    _registerCompanyDomain();
  }

  static void _registerCompanyData() {
    qontakCompanyDependency
      ..registerLazySingleton<CompanyRemoteDataSource>(
          () => CompanyRemoteDataSourceImpl(baseApi: qontakCommonDependency()))
      ..registerLazySingleton<CompanyRepository>(
          () => CompanyRepositoryImpl(remoteDataSource: qontakCompanyDependency()));
  }

  static void _registerCompanyDomain() {
    qontakCompanyDependency
      ..registerLazySingleton(() => GetCompanyUseCase(repository: qontakCompanyDependency()))
      ..registerLazySingleton(() => AddCompanyUseCase(repository: qontakCompanyDependency()));
  }
}
```

Registration order within a feature: Database/ObjectBox → Data sources → Repositories → Use cases.

---

## Creation Order <!-- 12 -->

```
1. features/<pkg>/lib/src/data/models/remote/<concept>_response.dart  ← API response DTO
   features/<pkg>/lib/src/data/models/remote/<concept>_request.dart   ← API request body (if POST/PUT)
   features/<pkg>/lib/src/data/models/local/<concept>_db.dart         ← DB record (if local persistence)
2. features/<pkg>/lib/src/data/mappers/<concept>_mapper.dart           ← Mapper
3. features/<pkg>/lib/src/data/data_sources/remote/<feature>_remote_data_source.dart
4. features/<pkg>/lib/src/data/repositories/<feature>_repository_impl.dart
```

Run `dart run build_runner build --delete-conflicting-outputs` in the feature package after creating DTO models.
