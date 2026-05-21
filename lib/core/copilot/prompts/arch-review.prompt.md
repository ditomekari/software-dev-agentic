---
mode: agent
tools:
  - codebase
  - readFile
  - search
description: "Audit a feature, file, or the full codebase for Clean Architecture violations — layer boundaries, entity purity, BLoC patterns, DI rules, naming."
---

Audit the Dart code at `$ARGUMENTS` for Clean Architecture violations. If no scope is provided, ask the user: specific file, feature folder, or full codebase.

## Audit Checklist

Work through each rule. Report every violation with: **file path**, **line number**, **rule**, and **suggested fix**.

---

### U1 — Layer Import Direction
Search for:
- Domain files importing `package:dio`, `package:flutter_bloc`, `*Response`, `*Db`, `*DataSource`
- Data files importing BLoC/Cubit types or `package:flutter/material.dart`
- Presentation files importing `*RepositoryImpl`, `*DataSourceImpl`, or DTO types

### U2 — Entity Immutability
Search entities for: `@JsonSerializable`, `fromJson`, methods that mutate state, missing `@freezed`, `.g.dart` part directives.

### U3 — Service / UseCase Purity
Search use cases and domain services for imports of framework packages or data-layer types.

### U4 — Mapper Isolation
Search mappers for calls to other mappers or for data-source fetch calls.

### U5 — Naming Conventions
- UseCase classes must end in `UseCase`
- Entity classes must NOT end in `Entity`
- BLoC state classes must use `@freezed`

### U6 — Entity Field Leakage
Search entity files for `Map<String,` or `dynamic` fields. For each: verify whether a typed value object or enum already exists. If yes → it must be used. If no → the untyped field is a violation.

### U6b — Relation Cardinality
Search entity files for `List<String>` (or other `List<primitive>`). For each: is the cardinality fixed (domain-defined at compile time) or open/backend-configurable? Fixed → should be a named nullable typed field. Open → `List<TypedValueObject>`.

### U7 — UI State in Entity
Search entity files for `bool ` and `bool?` fields. For each: who sets this value after construction? If set by a user action (tap, toggle, selection) → belongs in BLoC state, not the entity.

### U8 — Screen as BLoC Orchestrator
Search screen files for `context.read<` inside `BlocListener` callbacks or `listenWhen` predicates. The listener must only trigger navigation, toasts, or analytics — business logic belongs in a BLoC event handler.

### U9 — App-Scoped BLoC Watched in Build
Search for `context.watch<` and `BlocBuilder<` in screen files. For each BLoC found, search `route_manager.dart` — if the BLoC appears in the app-root `MultiBlocProvider` (not inside a specific route builder), it is app-scoped. Flag if the widget rebuilds more frequently than necessary.

### U10 — Nested BlocConsumer / BlocBuilder
Search files containing both `BlocConsumer` and `BlocBuilder` or multiple `BlocConsumer` at different nesting levels. Evaluate whether the inner one can be extracted to a separate widget with a tighter `buildWhen`.

---

## Output Format

```
### Critical
- `path/to/file.dart:42` **U8** — `context.read<XxxBloc>().add(...)` inside listener. Move business logic to a BLoC event handler.

### Warning
- `path/to/entity.dart:15` **U6** — field `tags` is `List<String>` — use `List<Tag>` typed value object if one exists.

### Info
- `path/to/usecase.dart:8` **U5** — class `LoadCompany` should be `LoadCompanyUseCase`.
```

If no violations found: `✓ No Clean Architecture violations found in scope.`
