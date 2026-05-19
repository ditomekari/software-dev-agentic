# CLAUDE.md

<!-- BEGIN software-dev-agentic:flutter-mobile-jurnal -->
Flutter · Clean Architecture + BLoC · get_it/injectable

## Architecture

Module structure and path conventions: `.claude/reference/`

## Principles

Clean Architecture · DRY · SOLID — apply to all new code.

**Layer dependency rule:** Presentation → Domain ← Data. Domain depends on nothing.

## Workflow

Use trigger skills as entry points — `/builder-build-feature`, `/auditor-arch-review`, `/detective-debug`, etc.

**Feature work → always start with `/builder-build-feature`, never inline.**

## Dart Knowledge

If `.claude/dart-knowledge.yaml` exists and the task requires understanding existing Dart APIs, components, or features — query `dart-knowledge-query` for context before writing code.
<!-- END software-dev-agentic:flutter-mobile-jurnal -->
