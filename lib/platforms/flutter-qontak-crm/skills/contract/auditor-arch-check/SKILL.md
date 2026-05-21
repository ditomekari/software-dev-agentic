---
name: auditor-arch-check
description: Check Flutter Qontak CRM Clean Architecture rules — BLoC patterns, manual GetIt DI (no @injectable), ViewDataState API, layer import direction, naming conventions, and dual-DB awareness. Called by auditor-arch-review-worker.
user-invocable: false
tools: Read, Glob, Grep
---

Check the provided files against Flutter Qontak CRM–specific architecture rules. Report violations with file path, line number, and fix.

## Layer Import Rules

- Domain: no `package:dio`, no `package:mekari_network`, no `package:flutter_bloc`, no `*Response`/`*Db`/`*DataSource` imports
- Data: no BLoC/Cubit imports, no `package:flutter/material.dart`
- Presentation: no `RepositoryImpl`, no `DataSourceImpl`, no DTO types (`*Response`, `*Request`, `*Db`)

## DI Rules — Manual GetIt, No @injectable

- No `@injectable`, `@lazySingleton`, `@singleton`, `@factoryMethod` annotations anywhere
- Use cases, data sources, repositories: `registerLazySingleton<Interface>(() => Impl(...))` in the feature's `<Feature>Dependency` class
- BLoCs are NOT registered in get_it — they are instantiated inline in `route_manager.dart` inside `BlocProvider`
- Feature DI accessor pattern: `final qontak<Feature>Dependency = GetIt.instance;`

### DI Topology (use to audit BLoC scope violations)

CRM DI is structured in two layers:

**App-root layer:** A top-level `MultiBlocProvider` in `App` wraps the entire widget tree. BLoCs listed here are **app-scoped** — they live for the entire session and are accessible from any screen. Accessing a BLoC here from a `BlocBuilder` or `context.watch<>()` will re-render on every state change across the app. If the BLoC changes frequently (e.g. a connection-status cubit), watching it in a build method is expensive.

**Route layer:** `route_manager.dart` contains route-specific `BlocProvider` instantiations. BLoCs declared here are **screen-scoped** — they are created when the route is pushed and disposed when it is popped. These are the correct location for feature BLoCs.

**Audit rule for U9 (Global BLoC watched in build):** When you see `context.watch<XxxBloc>()` or `BlocBuilder<XxxBloc, ...>`, `Grep` `route_manager.dart` for the BLoC class name. If it appears in the app-root `MultiBlocProvider` (not inside a route builder), it is app-scoped. Then evaluate: does the screen widget rebuild more often than necessary? Flag if yes.

## Navigation Rules

- Navigation uses `Navigator` 1.0 — no `go_router`
- BLoC never calls navigation directly — navigation is a `BlocListener` side effect in the screen

## ViewDataState API Rules

Grep for incorrect patterns and flag:

- `state.*.isLoaded` → must be `state.*.status.isHasData`
- `state.*.hasError` → must be `state.*.status.isError`
- `state.*.isLoading` → must be `state.*.status.isLoading` (only in BlocListener/listenWhen)
- `ViewDataState.noData()` is valid for post-reset state

## BLoC Rules

- Constructor uses named parameters with `required` — no positional args
- Each handler emits `ViewDataState.loading()` first, then folds the result
- State uses `@freezed` with one `ViewDataState<T>` per async operation — no raw `isLoading` booleans
- `sequential()` transformer required for BLoCs handling load + loadMore + filter events

## UseCase Naming Rules

- UseCase naming: `<Verb><Entity>UseCase` — WITH `UseCase` suffix (e.g. `GetCompanyUseCase`, `AddCompanyUseCase`)
- Extends `UseCase<ReturnType, Params>` from `qontak_common`
- Returns `Future<Either<Failure, T>>`

## Error Handling Rules

- Repositories catch `Exception` and propagate via `TaskEither.tryCatch(...)` or manual `try/catch` returning `Left(Failure(...))`
- DataSources throw exceptions — they never return `Either`
- `QontakMonitor` logging: call `qontakCommonDependency<QontakMonitor>().logCrashMonitor(logName: ...)` in repo/datasource error handlers using a constant from the feature's logging constants file

## Naming Rules

Check against `lib/platforms/flutter-qontak-crm/reference/code-architecture/syntax-conventions-impl.md ## Naming Conventions`:

- Entity: no suffix (e.g. `Company` not `CompanyEntity`)
- UseCase: `<Verb><Entity>UseCase` suffix required
- Repository impl: `[Entity]RepositoryImpl` registered as `[Entity]Repository` abstract type
- BLoC event variant names are PascalCase action nouns (e.g. `LoadRemoteCompany`, `FilterCompany`)

## Dual-DB Migration Rules

- Features already in ObjectBox migration must implement both Isar and ObjectBox paths via `DataSourceSwapHelper.shouldUseObjectBox`
- New features: use ObjectBox only (Isar is legacy)

## Output

List each violation as:

- File: `<path>`
- Line: `<n>`
- Rule: `<rule name>`
- Fix: `<what to change>`

Report `PASS` if no violations found.
