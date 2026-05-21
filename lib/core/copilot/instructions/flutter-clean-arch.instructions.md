---
applyTo: "**/*.dart"
---

## Clean Architecture — Layer Import Rules

Layer import direction: Domain ← Data ← Presentation. Inner layers never import outer.

- **Domain** (`domain/`): no `package:dio`, `package:flutter_bloc`, `*Response`, `*Db`, `*DataSource` imports
- **Data** (`data/`): no BLoC/Cubit imports, no `package:flutter/material.dart`
- **Presentation** (`presentation/`): no `RepositoryImpl`, `DataSourceImpl`, DTO types (`*Response`, `*Request`, `*Db`)

## Entity Rules

- `@freezed` with `part '[concept].freezed.dart'` only — never `.g.dart`
- No `Entity` suffix — name after the business concept (`Company`, not `CompanyEntity`)
- No `@JsonSerializable`, no `fromJson`/`toJson` — entities are pure domain objects
- No `Map<String, dynamic>` or `dynamic` fields — use typed value objects or enums
- No `bool` fields set by user interaction (taps, toggles) — those belong in BLoC state
- Relationship collections: `List<TypedValueObject>`, not `List<String>`
- Nullable `T?` only when the domain genuinely allows absence

**Before writing any field type:** search for existing enums, value objects, and typed IDs in the domain layer. Use what exists; create new types only when both semantic search and text search confirm absence.

## BLoC Rules

- One BLoC per screen — a second BLoC requires independent async lifecycle, cross-screen reuse, or orthogonal failure paths
- Constructor uses named `required` parameters — no positional args
- Each event handler emits `ViewDataState.loading()` first, then folds the result
- State uses `@freezed` with one `ViewDataState<T>` per async operation — no raw `isLoading` booleans

## ViewDataState API

Always use:
- `.status.isHasData` — NOT `.isLoaded`
- `.status.isError` — NOT `.hasError`
- `.status.isLoading` — only in `listenWhen` / `BlocListener`
- `ViewDataState.noData()` is valid for post-reset state

## UseCase Naming

`<Verb><Entity>UseCase` with `UseCase` suffix — e.g. `GetCompanyUseCase`, `AddContactUseCase`.

## Error Handling

- Repositories catch exceptions and map to `Failure` — never expose raw exceptions
- DataSources throw `AppException` — they never return `Either`
- BLoCs use `result.fold()` — no unhandled exceptions reach the widget tree
