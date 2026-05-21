---
applyTo: "**/*.dart"
---

## CRM DI — Manual GetIt, No @injectable

- No `@injectable`, `@lazySingleton`, `@singleton`, `@factoryMethod` annotations anywhere
- UseCases, DataSources, Repositories: `registerLazySingleton<Interface>(() => Impl(...))` in the feature's `<Feature>Dependency` class
- BLoCs are **not** registered in GetIt — instantiated inline in `route_manager.dart` inside `BlocProvider`
- DI accessor pattern: `final qontakXxxDependency = GetIt.instance`
- Page Init UseCases: injected via `QontakXxxDependency` constructor, same `registerLazySingleton` pattern

## CRM BLoC Scope

BLoCs are wired via `MultiBlocProvider` in `route_manager.dart`:
- **Screen-scoped**: declared inside a route builder → disposed when route is popped ✓
- **App-scoped**: declared in top-level `MultiBlocProvider` in `App` → lives for entire session

Never provide a screen-specific BLoC at app root. To determine scope: search `route_manager.dart` for the BLoC class name — if it appears in the outer `MultiBlocProvider` (not inside a specific route's builder), it is app-scoped.

`context.watch<>()` on an app-scoped BLoC causes the widget to rebuild on every state change across the app — use `BlocSelector` or `context.read<>()` where full reactivity is not needed.

## CRM Navigation

- `Navigator` 1.0 only — no `go_router`
- BLoC never calls navigation directly — navigation is always a `BlocListener` side effect in the screen
- `BlocProvider` for route-scoped BLoCs lives in `route_manager.dart`, not inside screen widgets

## CRM Screen initState Pattern

Pull the BLoC from the dependency accessor in `initState` — not from `context`:
```dart
@override
void initState() {
  super.initState();
  _bloc = qontakFeatureDependency<FeatureBloc>()
    ..add(const FeatureEvent.loadData());
}
```

## CRM Page Init UseCase (multi-repository screens)

When a screen needs data from 2+ repositories, use a `GetXxxPageDataUseCase` that returns `XxxPageData`:
- `XxxPageData`: `@freezed` class in `domain/read_models/`, contains entity references only
- Registered via `registerLazySingleton` in `QontakXxxDependency`
- BLoC holds one `ViewDataState<XxxPageData>` for the entire page load

## CRM Multi-Source Mapping

Repository is the only layer that merges multiple sources. Each mapper receives exactly one input type. Canonical domain terms only — no API-originated names in entities.
