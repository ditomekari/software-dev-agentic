# Flutter — Navigation (go_router)

> Canonical terms and invariants: `reference/code-architecture/ui-theory.md` — `## Navigator / Coordinator` section.

`go_router` is the standard Flutter navigation solution — declarative, deep-link ready, and type-safe with code generation.

---

## Setup <!-- 9 -->

```yaml
dependencies:
  go_router: ^14.0.0
```

---

## Route Constants <!-- 26 -->

Define all route paths and names as constants. Never hard-code path strings.

```dart
// presentation/navigation/routes.dart
abstract class Routes {
  Routes._();

  // Auth
  static const String login = '/login';
  static const String forgotPassword = '/forgot-password';

  // Employee
  static const String employees = '/employees';
  static const String employeeDetail = '/employees/:id';
  static const String employeeEdit = '/employees/:id/edit';

  // Helpers for parameterised paths
  static String employeeDetailPath(String id) => '/employees/$id';
  static String employeeEditPath(String id) => '/employees/$id/edit';
}
```

---

## Router Configuration <!-- 62 -->

```dart
// presentation/navigation/app_router.dart
import 'package:go_router/go_router.dart';
import 'package:injectable/injectable.dart';
import '../../di/injection.dart';
import '../screens/employee_list_screen.dart';
import '../screens/employee_detail_screen.dart';
import '../screens/login_screen.dart';
import 'routes.dart';

@singleton
class AppRouter {
  AppRouter({required this.authCubit});

  final AuthCubit authCubit;

  late final router = GoRouter(
    initialLocation: Routes.employees,
    redirect: _guard,
    routes: [
      GoRoute(
        path: Routes.login,
        builder: (_, __) => const LoginScreen(),
      ),
      GoRoute(
        path: Routes.employees,
        builder: (_, __) => const EmployeeListScreen(),
        routes: [
          GoRoute(
            path: ':id',
            builder: (_, state) => EmployeeDetailScreen(
              employeeId: state.pathParameters['id']!,
            ),
            routes: [
              GoRoute(
                path: 'edit',
                builder: (_, state) => EmployeeEditScreen(
                  employeeId: state.pathParameters['id']!,
                ),
              ),
            ],
          ),
        ],
      ),
    ],
  );

  String? _guard(BuildContext context, GoRouterState state) {
    final isAuthenticated = authCubit.state.isAuthenticated;
    final isOnLoginPage = state.matchedLocation == Routes.login;

    if (!isAuthenticated && !isOnLoginPage) return Routes.login;
    if (isAuthenticated && isOnLoginPage) return Routes.employees;
    return null;
  }
}
```

---

## Navigating from Widgets <!-- 18 -->

```dart
// Push a new screen
context.push(Routes.employeeDetailPath(employee.id));

// Replace current screen (no back button)
context.go(Routes.login);

// Pop to previous screen
context.pop();

// Pop with a result
context.pop(true);
```

---

## Navigating from BLoC (Side Effects) <!-- 43 -->

Use `BlocListener` — BLoC emits a navigation action via state, widget listens and calls `context.go/push`.

```dart
// In BLoC state — add a navigation field
@freezed
class EmployeeState with _$EmployeeState {
  const factory EmployeeState({
    required ViewDataState<EmployeeEntity> employeeState,
    @Default(null) EmployeeNavAction? navAction,
  }) = _EmployeeState;
}

sealed class EmployeeNavAction {
  const factory EmployeeNavAction.goToEdit(String employeeId) =
      GoToEditAction;
  const factory EmployeeNavAction.popAfterDelete() = PopAfterDeleteAction;
}
```

```dart
// In Screen
BlocListener<EmployeeBloc, EmployeeState>(
  listenWhen: (prev, curr) => prev.navAction != curr.navAction,
  listener: (context, state) {
    final action = state.navAction;
    if (action == null) return;
    switch (action) {
      case GoToEditAction(:final employeeId):
        context.push(Routes.employeeEditPath(employeeId));
      case PopAfterDeleteAction():
        context.pop();
    }
    // Clear after handling
    context.read<EmployeeBloc>().add(const EmployeeEvent.clearNavAction());
  },
  child: ...,
)
```

---

## Passing Complex Objects <!-- 28 -->

For objects too large or non-serialisable to encode in the URL, use `extra`:

```dart
// Navigate with extra
context.push(
  Routes.employeeDetailPath(employee.id),
  extra: employee,
);

// Receive in builder
GoRoute(
  path: ':id',
  builder: (_, state) {
    final employee = state.extra as EmployeeEntity?;
    return EmployeeDetailScreen(
      employeeId: state.pathParameters['id']!,
      prefetchedEmployee: employee,
    );
  },
),
```

**Note:** `extra` is lost on deep link or hot restart. Always have a fallback to fetch from the use case using the path parameter ID.

---

## Nested Navigation (Shell Routes) <!-- 23 -->

Use `ShellRoute` for persistent navigation bars:

```dart
GoRoute(
  path: '/',
  builder: (_, state) => const ShellScaffold(child: HomeTab()),
  routes: [
    ShellRoute(
      builder: (_, state, child) => MainScaffold(child: child),
      routes: [
        GoRoute(path: '/home', builder: (_, __) => const HomeTab()),
        GoRoute(path: '/profile', builder: (_, __) => const ProfileTab()),
        GoRoute(path: '/settings', builder: (_, __) => const SettingsTab()),
      ],
    ),
  ],
),
```

---

## Deep Link Support <!-- 16 -->

```dart
// android/app/src/main/AndroidManifest.xml
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="https" android:host="example.com" />
</intent-filter>
```

go_router handles deep links automatically when paths match route definitions. No extra configuration needed in Dart.

---

## Material App Setup <!-- 21 -->

```dart
// app.dart
import 'package:flutter/material.dart';
import 'di/injection.dart';
import 'presentation/navigation/app_router.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: getIt<AppRouter>().router,
      title: 'My App',
      theme: ThemeData(...),
    );
  }
}
```
