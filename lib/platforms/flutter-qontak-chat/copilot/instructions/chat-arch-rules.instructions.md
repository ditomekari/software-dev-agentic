---
applyTo: "**/*.dart"
---

## Chat DI — @injectable

- Feature UseCases/Repositories/DataSources: `@lazySingleton` or `@singleton` annotation — code generator auto-wires constructor dependencies
- BLoCs: use `registerFactory` in `MainDependency._registerPresentation()` — NOT `@injectable` on BLoC classes
- Feature packages (`chat_*`) expose static `register*()` methods; resolved via typed accessors (`coreDependency<T>()`, `inboxDependency<T>()`, etc.)
- `BlocProvider` for route-scoped BLoCs lives in `route_manager.dart`, NOT inside screen widgets

## Chat BLoC Scope

- **Screen-scoped**: declared inside route builders in `route_manager.dart` → disposed when route popped ✓
- **App-scoped**: declared in `AppWidget` top-level `MultiBlocProvider` → lives for entire session

Never provide a screen-specific BLoC at app root. To determine scope: search `route_manager.dart` and `AppWidget` for the BLoC class name.

`context.watch<>()` on an app-scoped BLoC causes the widget to rebuild on every state change — use `BlocSelector` or `context.read<>()` where full reactivity is not needed.

## Chat Navigation

- `Navigator` 1.0 / `AppRouteManger` / `NavigationHelper.pushNamed` — no `go_router`
- BLoC never calls `NavigationHelper` directly — navigation is always a `BlocListener` side effect

## Chat Error Mapping

Repositories catch exceptions and map via `CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error)` — NOT `AppException.toFailure()`.

## Chat Page Init UseCase (multi-repository screens)

When a screen needs data from 2+ repositories, use a `GetXxxPageDataUseCase` that returns `XxxPageData`:
- Annotate with `@lazySingleton` — injectable codegen wires sub-UseCase constructor dependencies automatically
- `XxxPageData`: `@freezed` class in `domain/read_models/`, contains entity references only
- BLoC holds one `ViewDataState<XxxPageData>` for the entire page load

## Chat Multi-Source Mapping

Repository is the only layer that merges multiple sources. Use `@LazySingleton(as: XxxRepository)` on the `RepositoryImpl`. Each mapper receives exactly one input type. Canonical domain terms only — no API-originated names in entities.
