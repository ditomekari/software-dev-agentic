# Flutter Qontak — Module-to-Module Communication

> Feature packages must NOT directly depend on each other.
> The app module uses two patterns: **Module API** (for data sharing) and **Typedef Callback Injection** (for UI/behavior sharing at the DI layer).

---

## Typedef Callback Injection (Primary Pattern) <!-- 38 -->

In `mobile-qontak-chat`, cross-package UI behavior is shared by passing typed functions (typedefs) during DI registration in `ChatDi`. This is the main pattern for the app module.

The feature package declares a typedef for what it needs, and the app provides the concrete implementation:

```dart
// In chat_composer package — declares what it needs:
typedef GetVideoViewerFn = Widget Function({required String videoPath});
typedef GetDocumentViewerFn = Widget Function({required String filePath});

// In chat_di.dart — the app provides the implementations:
ComposerDependency.registerComposer(
  getVideoViewer: _getVideoViewer,          // app wires these
  getDocumentViewerWidget: _getDocumentViewerWidget,
  getPreviewBubbleWidget: _getPreviewBubbleWidget,
  // ...
);

// The app implements the typedefs using its own packages:
static Widget _getVideoViewer({required String videoPath}) =>
    VideoViewer(videoPath: videoPath);  // uses chat_conversation widget

static Widget _getDocumentViewerWidget({required String filePath}) =>
    DocumentViewer(filePath: filePath);
```

This allows `chat_composer` to display a video viewer without importing `chat_conversation` directly.

---

## Module API Pattern (for Data Sharing) <!-- 77 -->

## Module API Pattern <!-- 77 -->

When Feature A needs data/behavior from Feature B:

1. Define an abstract `*ModuleApi` in `[prefix]_core`
2. Implement it in Feature B
3. Register the impl in Feature B's DI
4. Feature A injects the abstract `*ModuleApi` — no direct dependency on Feature B

### Step 1 — Abstract API in core

```dart
// shared/[prefix]_core/lib/src/module_api/employee_module_api.dart
abstract class EmployeeModuleApi {
  Future<EmployeeDetail?> getEmployeeDetail(String empId);
  String getEmployeeIdFormat();
}
```

Export from core barrel:

```dart
// shared/[prefix]_core/lib/[prefix]_core.dart
export 'src/module_api/employee_module_api.dart';
```

### Step 2 — Implementation in the owning feature

```dart
// features/[prefix]_employee/lib/src/module_api/employee_module_api_impl.dart
import 'package:[prefix]_core/[prefix]_core.dart';
import '../domain/usecases/get_employee_detail.dart';

@LazySingleton(as: EmployeeModuleApi)  // registered as abstract type
class EmployeeModuleApiImpl implements EmployeeModuleApi {
  EmployeeModuleApiImpl(this._getEmployeeDetail);

  final GetEmployeeDetail _getEmployeeDetail;

  @override
  Future<EmployeeDetail?> getEmployeeDetail(String empId) async {
    final result = await _getEmployeeDetail(GetEmployeeDetailParams(id: empId));
    return result.fold((_) => null, (e) => e);
  }

  @override
  String getEmployeeIdFormat() => 'EMP-000000';
}
```

### Step 3 — Consumer feature injects the abstraction

```dart
// features/[prefix]_payslip/lib/src/presentation/blocs/payslip_bloc.dart
@injectable
class PayslipBloc extends Bloc<PayslipEvent, PayslipState> {
  PayslipBloc(this._getPayslips, this._employeeApi) : super(...);

  final GetPayslips _getPayslips;
  final EmployeeModuleApi _employeeApi;   // ← abstract, no import of employee package
}
```

**pubspec.yaml of payslip module:**

```yaml
# features/[prefix]_payslip/pubspec.yaml
dependencies:
  [prefix]_core:           # contains EmployeeModuleApi abstraction
    path: ../../shared/[prefix]_core
  [prefix]_dependencies:
    path: ../../shared/[prefix]_dependencies
# ❌ NO direct dep on [prefix]_employee
```

---

## When to Use Module API vs. Shared Core <!-- 11 -->

| Scenario | Approach |
|---|---|
| Pure utility / formatting logic | Move to `[prefix]_core` directly |
| Data that lives in another feature's DB/API | Module API pattern |
| UI component shared between features | Shared Widget in `[prefix]_core` |
| Two features share an entire domain | Merge them into one feature module |

---

## Navigation Between Modules <!-- 30 -->

Modules must not push routes from other modules directly. Use an abstract
navigation class in `[prefix]_core`:

```dart
// shared/[prefix]_core/lib/src/module_api/auth_navigation_api.dart
abstract class AuthNavigationApi {
  void goToLogin(BuildContext context);
  void goToForgotPassword(BuildContext context);
}
```

Implement in the auth feature:

```dart
// features/[prefix]_auth/lib/src/module_api/auth_navigation_api_impl.dart
@LazySingleton(as: AuthNavigationApi)
class AuthNavigationApiImpl implements AuthNavigationApi {
  @override
  void goToLogin(BuildContext context) => context.goNamed('login');

  @override
  void goToForgotPassword(BuildContext context) =>
      context.goNamed('forgotPassword');
}
```

Any module injects `AuthNavigationApi` to navigate to auth screens without
knowing the route names or the auth package's internals.
