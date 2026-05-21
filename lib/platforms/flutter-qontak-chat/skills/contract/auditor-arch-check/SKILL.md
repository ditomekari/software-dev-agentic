---
name: auditor-arch-check
description: Check Flutter Qontak Clean Architecture rules — BLoC patterns, manual GetIt DI, Navigator 1.0 usage, ViewDataState API, layer import direction, and naming conventions. Called by auditor-arch-review-worker.
user-invocable: false
tools: Read, Glob, Grep
---

Check the provided files against Flutter Qontak-specific architecture rules. Report violations with file path, line number, and fix.

## Layer Import Rules

- Domain: no `package:dio`, no `package:flutter_bloc`, no `*Response`/`*Db`/`*DataSource` imports
- Data: no BLoC/Cubit imports, no `package:flutter/material.dart`
- Presentation: no `RepositoryImpl`, no `DataSourceImpl`, no DTO types

## DI Rules — No `@injectable` in App Module

- BLoCs must use `registerFactory` in `MainDependency._registerPresentation()` — never `@injectable`
- DataSources/Repositories/UseCases use `registerLazySingleton` — never `@injectable` in app module
- Feature packages (`chat_*`) expose static `register*()` methods; resolved via typed accessors (`coreDependency<T>()`, `inboxDependency<T>()`, etc.)
- `BlocProvider` for route-scoped BLoCs lives in `route_manager.dart`, NOT inside screen widgets

### DI Topology (use to audit BLoC scope violations)

Chat DI is structured in two layers:

**App-root layer:** `AppWidget` (or the top-level `MultiBlocProvider`) wraps the entire widget tree with globally-shared BLoCs/Cubits — e.g. connectivity status, auth session, unread counts. These are **app-scoped**: they live for the entire session. Accessing an app-scoped BLoC via `context.watch<>()` or `BlocBuilder` in a leaf widget causes that widget to rebuild on every state change across the app.

**Route layer:** `route_manager.dart` contains route-specific `BlocProvider` entries. BLoCs here are **screen-scoped** — created when the route is pushed, disposed when popped. All feature-level BLoCs belong here, not at app root.

**Audit rule for U9 (Global BLoC watched in build):** When you see `context.watch<XxxBloc>()` or `BlocBuilder<XxxBloc, ...>`, `Grep` `route_manager.dart` and `AppWidget` for the BLoC class name. If it appears in an app-root provider (not inside a specific route builder), it is app-scoped. Then evaluate: does the widget rebuild more often than necessary? Flag if yes.

## Navigation Rules

- Navigation uses `Navigator` 1.0 / `AppRouteManger` / `NavigationHelper.pushNamed` — no `go_router`
- BLoC never calls `NavigationHelper` directly — navigation is a `BlocListener` side effect in the screen

## ViewDataState API Rules

Grep for incorrect patterns and flag:
- `state.*.isLoaded` → must be `state.*.status.isHasData`
- `state.*.hasError` → must be `state.*.status.isError`
- `state.*.isLoading` → must be `state.*.status.isLoading` (in BlocListener/listenWhen)
- `ViewDataState.noData()` is valid for post-reset state

## BLoC Rules

- Constructor uses named parameters with `required` — no positional args
- Each handler emits `ViewDataState.loading()` first, then folds the result
- State uses `@freezed` with one `ViewDataState<T>` per async operation — no raw `isLoading` booleans

## Error Handling Rules

- Repositories catch `Exception` and map via `CoreMapperExceptionToFailure.mapExceptionToFailure(exception: error)` — not `AppException.toFailure()`
- DataSources throw `AppException` — they never return `Either`
- BLoCs use `result.fold()` — no unhandled exceptions reach the widget tree

## Naming Rules

Check against `lib/platforms/flutter-qontak-chat/reference/code-architecture/syntax-conventions-impl.md ## Naming Quick-Reference`:
- Entity: no `Entity` suffix (e.g. `Conversation` not `ConversationEntity`)
- UseCase: verb-only, no `UseCase` suffix (e.g. `GetInbox` not `GetInboxUseCase`)
- Repository impl: `[Concept]RepositoryImpl` registered as `[Concept]Repository` abstract type

## Output

List each violation as:
- File: `<path>`
- Line: `<n>`
- Rule: `<rule name>`
- Fix: `<what to change>`

Report `PASS` if no violations found.
