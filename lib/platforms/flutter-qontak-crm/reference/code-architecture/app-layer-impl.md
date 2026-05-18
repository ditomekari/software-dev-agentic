# Flutter Qontak CRM — App Layer

> Concepts and invariants: `lib/core/reference/code-architecture/app-layer-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

The app module (`lib/`) is the app-shell only — auth, bottom navigation, DI orchestration, routing. All feature code lives in `features/`.

---

## Initialization Order <!-- 15 -->

`engine.dart` owns the boot sequence:

```
main.dart
  └── engine.dart
        1. Firebase.initializeApp()
        2. ObjectBoxInitializer.init()   ← ObjectBox store setup
        3. CrmDi.initDependency()        ← GetIt registration
        4. runApp(CrmApp())
```

```dart
// lib/engine.dart
Future<void> initEngine() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  await ObjectBoxInitializer.init();
  await CrmDi.initDependency();
  runApp(const CrmApp());
}
```

---

## CrmDi (DI Orchestrator) <!-- 20 -->

```dart
// lib/configs/di/crm_di.dart
class CrmDi {
  static Future<void> initDependency() async {
    // 1. Register common + await ready
    QontakCommonDependency.registerCommon();
    await GetIt.instance.allReady();

    // 2. Register core
    QontakCoreDependency.registerCore();

    // 3. Register feature dependencies (order within this group does not matter)
    QontakCompanyDependency.registerCompany();
    QontakContactDependency.registerContact();
    QontakDealDependency.registerDeal();
    QontakTaskDependency.registerTask();
    QontakNoteDependency.registerNote();
    QontakTicketDependency.registerTicket();
    QontakProductDependency.registerProduct();
    QontakLiveGpsDependency.registerLiveGps();
    QontakMiscDependency.registerMisc();

    // 4. Register app-level (depends on all above)
    QontakCrmDependency.registerApp();
  }
}
```

When adding a new feature package: add its `Dependency.register*()` call in step 3 above.

---

## App Entry Point <!-- 10 -->

```dart
// lib/app.dart
class CrmApp extends StatelessWidget {
  const CrmApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Qontak CRM',
      theme: CrmTheme.light,
      onGenerateRoute: RouteManager.onGenerateRoute,
      localizationsDelegates: [
        ...featureModules.map((m) => m.localizationsDelegate()).whereType(),
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('id'), Locale('en')],
    );
  }
}
```

---

## featureModules List <!-- 12 -->

```dart
// lib/configs/modules.dart
final List<BaseModule> featureModules = [
  CRMCompanyModule(),
  CRMContactModule(),
  CRMDealModule(),
  CRMTaskModule(),
  CRMNoteModule(),
  CRMTicketModule(),
  CRMProductModule(),
  CRMLiveGpsModule(),
  QontakCommonModule(),
];
```

Each `BaseModule` provides: `LocalizationsDelegate` for the active flavor + `CollectionSchema` list for Isar.

---

## BaseModule Pattern <!-- 12 -->

```dart
// features/crm_company/lib/src/crm_company.dart
class CRMCompanyModule implements BaseModule {
  @override
  LocalizationsDelegate? localizationsDelegate() {
    if (FlavorChecker.isPyridam) return PyridamCompanyLocalizations.delegate;
    return CompanyLocalizations.delegate;
  }

  @override
  List<CollectionSchema> collectionSchemas() => [CompanyDbSchema];
}
```

---

## App-Shell Concerns <!-- 10 -->

The application module's own `lib/data/`, `lib/domain/`, `lib/presentation/` contain only app-shell features:

| Concern | Location |
|---|---|
| Auth token (login/logout) | `lib/data/`, `lib/domain/` |
| Login BLoC | `lib/presentation/bloc/login/` |
| Bottom navigation BLoC | `lib/presentation/bloc/bottom_nav/` |
| Entry screens (splash, login, main) | `lib/presentation/screens/` |
| App-level DI | `lib/configs/di/qontak_crm_dependency.dart` |
| Route manager | `lib/presentation/route_manager.dart` |

Feature code belongs exclusively in `features/<pkg>/`.
