# Flutter Qontak CRM — Navigation

> Concepts and invariants: `lib/core/reference/code-architecture/navigation-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

Navigation uses Flutter Navigator 1.0 — no `go_router`. The `route_manager.dart` in `lib/presentation/` is the single routing authority.

---

## Route Constants <!-- 10 -->

```dart
// lib/configs/constants/app_route.dart
abstract class AppRoute {
  AppRoute._();
  static const String company = '/company';
  static const String companyDetail = '/company/detail';
  static const String contact = '/contact';
  static const String deal = '/deal';
  static const String login = '/login';
  static const String main = '/main';
}
```

---

## route_manager.dart Pattern <!-- 20 -->

All `BlocProvider` wiring for route-scoped BLoCs lives in `route_manager.dart`. The screen never owns its own `BlocProvider`.

```dart
// lib/presentation/route_manager.dart
Route<dynamic>? onGenerateRoute(RouteSettings settings) {
  switch (settings.name) {
    case AppRoute.company:
      return MaterialPageRoute(
        settings: settings,
        builder: (_) => BlocProvider(
          create: (_) => CompanyBloc(
            getCompanyListUseCase: qontakCompanyDependency(),
            filterCompanyUseCase: qontakCompanyDependency(),
          ),
          child: const CompanyScreen(),
        ),
      );

    case AppRoute.companyDetail:
      final args = settings.arguments as CompanyDetailArgument;
      return MaterialPageRoute(
        settings: settings,
        builder: (_) => MultiBlocProvider(
          providers: [
            BlocProvider(
              create: (_) => CompanyDetailBloc(
                getCompanyByIdUseCase: qontakCompanyDependency(),
              ),
            ),
            BlocProvider(
              create: (_) => NoteListBloc(
                getNoteListUseCase: qontakNoteDependency(),
              ),
            ),
          ],
          child: CompanyDetailScreen(argument: args),
        ),
      );

    default:
      return null;
  }
}
```

---

## Screen Arguments Pattern <!-- 12 -->

```dart
// lib/src/presentation/screens/company_detail/company_detail_argument.dart
class CompanyDetailArgument {
  const CompanyDetailArgument({required this.companyId, this.companyName});
  final String companyId;
  final String? companyName;
}
```

Arguments are passed as `settings.arguments` and cast in `route_manager.dart`. Never pass domain entities directly — pass IDs and let the screen's BLoC fetch.

---

## Navigation Calls <!-- 12 -->

Navigation side effects belong in `BlocListener` — BLoC never calls navigation directly.

```dart
// From a screen (push)
Navigator.of(context).pushNamed(
  AppRoute.companyDetail,
  arguments: CompanyDetailArgument(companyId: company.id),
);

// Replace (e.g. after login)
Navigator.of(context).pushReplacementNamed(AppRoute.main);

// Pop
Navigator.of(context).pop();

// Pop with result
Navigator.of(context).pop(true);
```

---

## BLoC → Navigation Side Effect Pattern <!-- 10 -->

```dart
BlocListener<CompanyBloc, CompanyState>(
  listenWhen: (prev, curr) => prev.addCompanyState != curr.addCompanyState,
  listener: (context, state) {
    if (state.addCompanyState.status.isHasData) {
      Navigator.of(context).pop(true); // signal success to caller
    } else if (state.addCompanyState.status.isError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.addCompanyState.message ?? 'Failed')),
      );
    }
  },
  child: ...,
)
```

**Rules:**
- No `go_router` — Navigator 1.0 only
- BLoC never calls `Navigator` — navigation is always a `BlocListener` side effect in the screen
- `BlocProvider` for route-scoped BLoCs lives in `route_manager.dart`, not in the screen widget
- Add new route constants to `AppRoute` before registering in `route_manager.dart`
