# CLAUDE.md

<!-- BEGIN software-dev-agentic:flutter-qontak-crm -->
Flutter · Melos Monorepo · Clean Architecture · BLoC · get_it (manual) · multi-flavor

## Architecture

App structure and module types: `.claude/reference/project.md`
Layer patterns (entity, BLoC, mapper, etc.): `.claude/reference/code-architecture/`

DI: manual `GetIt.registerLazySingleton`/`registerFactory` — no `injectable` annotations.
BLoCs: NOT registered in GetIt — instantiated inline in `route_manager.dart` via `BlocProvider`.
DI orchestration: `CrmDi` → `QontakXxxDependency` per feature package.
BLoC state checks: `.status.isHasData` / `.status.isError` / `.status.isLoading` (from `qontak_common`).

## Principles

Clean Architecture · DRY · SOLID — apply to all new code.

**Layer dependency rule:** Presentation → Domain ← Data. Domain depends on nothing.

**Module dependency rule:** App shell → Feature packages. Feature packages depend on `crm_core` / `qontak_common` only — never on each other directly. Cross-feature data is resolved at the DI layer.

**Feature placement rule:** All feature code lives under `features/<package_name>/lib/src/`. The app shell (`lib/`) contains only auth, bottom nav, DI orchestration, and routing.

## Workflow

Use trigger skills as entry points — `/builder-build-feature`, `/auditor-arch-review`, `/detective-debug`, etc.

**Feature work → always start with `/builder-build-feature`, never inline.**

## Dart Knowledge

If `.claude/dart-knowledge.yaml` exists and the task requires understanding existing Dart APIs, components, or features — query `dart-knowledge-query` for context before writing code.
<!-- END software-dev-agentic:flutter-qontak-crm -->
