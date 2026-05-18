# CLAUDE.md

<!-- BEGIN software-dev-agentic:flutter-qontak -->
Flutter · Modular Clean Architecture · BLoC · get_it (manual) · external feature packages

## Architecture

App structure and module types: `.claude/reference/project.md`
Layer patterns (entity, BLoC, mapper, etc.): `.claude/reference/code-architecture/`

Navigation: centralized `route_manager.dart` (Navigator 1.0, not go_router)
DI: manual `GetIt.registerFactory`/`registerLazySingleton` via `MainDependency` and `ChatDi`
BLoC state checks: `.status.isHasData` / `.status.isError` / `.status.isLoading` (from `qontak_common`)

## Principles

Clean Architecture · DRY · SOLID — apply to all new code.

**Layer dependency rule:** Presentation → Domain ← Data. Domain depends on nothing.

**Module dependency rule:** App → Feature packages (external pub deps). Feature packages do NOT depend on each other — cross-package callbacks are injected at the DI layer (in `ChatDi`).

## Workflow

Use trigger skills as entry points — `/builder-build-feature`, `/auditor-arch-review`, `/detective-debug`, etc.

**Feature work → always start with `/builder-build-feature`, never inline.**
<!-- END software-dev-agentic:flutter-qontak -->
