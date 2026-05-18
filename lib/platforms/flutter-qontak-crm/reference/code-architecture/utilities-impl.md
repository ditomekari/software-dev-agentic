# Flutter Qontak CRM — Utilities

> Concepts and invariants: `lib/core/reference/code-architecture/utilities-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

Shared infrastructure lives in `features/crm_core/` and `features/qontak_common/`. Access via the respective dependency accessor.

---

## QontakMonitor (Crash Monitoring) <!-- 15 -->

`QontakMonitor` wraps Firebase Crashlytics. Registered in `QontakCommonDependency` and accessed via `qontakCommonDependency`.

```dart
// In repository / data source error handlers:
qontakCommonDependency<QontakMonitor>().logCrashMonitor(
  logName: CompanyLogConstant.getCompany, // always use a constant
);

// For debug-only temporary logs (removed before commit):
qontakCommonDependency<QontakMonitor>().logCrashMonitor(
  logName: '[DebugTest][CompanyRepositoryImpl][getCompany] entry — id: $id',
);
```

Never use `print` or `debugPrint` in repository/data source code — use `QontakMonitor`.
`debugPrint` is acceptable only in BLoC/presentation code where `QontakMonitor` is inaccessible.

---

## BaseApi / mekari_network (HTTP Client) <!-- 18 -->

`BaseApi` (from internal `mekari_network` package) is the only HTTP client. Registered in `QontakCommonDependency`.

```dart
// Injected into RemoteDataSource via constructor
class CompanyRemoteDataSourceImpl implements CompanyRemoteDataSource {
  CompanyRemoteDataSourceImpl({required this.baseApi});
  final BaseApi baseApi;

  Future<CompanyResponse> getCompany(String id) async {
    final response = await baseApi.get(Endpoint.company(id));
    return CompanyResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<CompanyResponse>> getCompanyList({CompanyFilterRequest? filter}) async {
    final response = await baseApi.get(
      Endpoint.companyList,
      queryParameters: filter?.toJson(),
    );
    final list = response.data as List<dynamic>;
    return list.map((e) => CompanyResponse.fromJson(e as Map<String, dynamic>)).toList();
  }
}
```

Endpoint constants are defined per feature in `lib/src/config/constants/endpoint.dart`:
```dart
abstract class Endpoint {
  Endpoint._();
  static String company(String id) => '/api/v1/crm/companies/$id';
  static const String companyList = '/api/v1/crm/companies';
}
```

---

## DatabaseService / Isar (Legacy) <!-- 12 -->

`DatabaseService` manages Isar. Available via `qontakCommonDependency<DatabaseService>()`. Use only in features not yet migrated to ObjectBox.

```dart
class CompanyIsarDatabase {
  CompanyIsarDatabase(this._databaseService);
  final DatabaseService _databaseService;

  Future<List<CompanyDb>> getAllCompanies() async {
    final isar = _databaseService.instance;
    return isar.companyDbs.where().findAll();
  }
}
```

---

## ObjectBoxStore (Migration Target) <!-- 12 -->

ObjectBox is the target local DB. Feature packages wrap it via `ObjectBoxStore`.

```dart
// features/crm_company/lib/src/config/objectbox/company_objectbox_store.dart
class CompanyObjectBoxStore {
  CompanyObjectBoxStore(this._store);
  final Store _store;

  Box<CompanyObjectBox> get box => _store.box<CompanyObjectBox>();
}
```

Registered per feature in the feature's DI class:
```dart
qontakCompanyDependency.registerLazySingleton<CompanyObjectBoxStore>(
  () => CompanyObjectBoxStore(qontakCommonDependency<ObjectBoxStore>().store),
);
```

---

## FlavorChecker <!-- 10 -->

For flavor-specific code paths:

```dart
if (FlavorChecker.isPyridam) {
  // Pyridam-specific logic or UI
}
if (FlavorChecker.isKrasSalesGo) {
  // KRAS SalesGo-specific path
}
// Default (main Qontak CRM): no check needed
```

---

## DataSourceSwapHelper <!-- 8 -->

Determines which local DB backend is active during the Isar → ObjectBox migration:

```dart
if (DataSourceSwapHelper.shouldUseObjectBox) {
  return _getFromObjectBox();
}
return _getFromIsar();
```

Use in local data source implementations only — never in repositories or domain.

---

## Asset Generation (flutter_gen) <!-- 8 -->

Assets are referenced via the generated `QontakCRMAssets` class:

```dart
import 'package:qontak_crm/gen/assets/assets.gen.dart';

// Usage
Image.asset(QontakCRMAssets.images.logo.path)
```

Never reference asset paths as raw strings. Never edit files under `lib/gen/`.

---

## Localization <!-- 8 -->

ARB files live per feature and per flavor under `lib/src/config/l10n/`. Accessed via the generated localization class:

```dart
// In widget
Text(CompanyLocalizations.of(context).companyListTitle)
```

Flavor-specific localizations are returned by the `BaseModule` implementation's `localizationsDelegate()`.
