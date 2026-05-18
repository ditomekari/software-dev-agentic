---
name: migrate-usecase
description: |
  Migrate Domain layer components to V2 architecture: old UseCase pattern → UseCaseProtocol with nested Params, legacy model structs → Domain Entities, root-level Repository protocols → Domain/Repository/. One component per run.
user-invocable: true
---

# Migrate UseCase to V2

Migrate one Domain layer component at a time to the modern architecture standard.

## Architecture Reference

Read these before starting:
- `.claude/reference/code-architecture/domain-impl.md` — V2 Domain patterns (entities, repo protocols, UseCases, Params)
- `.claude/reference/migration.md ## Legacy → Modern Code, ## UseCase Migration sections` — folder structure + UseCase migration guide
- `.claude/reference/code-architecture/di-impl.md` — DI Container wiring

## Scope

This skill covers **Domain layer only**:
- UseCase: `UseCase<Q,P,R>` typealias + separate Param files → `UseCaseProtocol` + nested `Params`
- Repository protocol: ensure it lives in `Domain/Repository/` (not root or legacy folders)
- Entity: extract from old model structs → `Domain/Entities/`
- DI wiring: register in module DIContainer after migration

**Out of scope for this skill:** DataSources, RepositoryImpl, Mappers (handled by `data-worker`), StateHolders/ViewModels (use `/migrate-presentation`).

## Safety Rules

⚠️ **BEFORE touching any file:**
1. Read the file — identify its current pattern (V1 legacy or V2 modern)
2. If already V2 — do nothing, report to user
3. Migrate **one component per run** (one UseCase, or one Repository protocol)
4. Run build after each file change before proceeding to the next
5. Never rename public-facing APIs (method names, type names) without user confirmation
6. Never delete old Param files until new nested Params are confirmed working

## What to Ask First

Before starting, ask the user:
1. Which file or component to migrate?
2. Is there an existing test file? (tests must stay green)
3. Is this module using DI Container yet? (affects wiring step)

## Implementation Steps

### Migrating a UseCase

**Step 1: Read the existing UseCase**
- Identify: old protocol type, separate Param files, `call()` vs `execute()` method
- Note all callers (ViewModels that use this UseCase)

**Step 2: Create migrated UseCase**
- New file at same path, same name
- Conform to `UseCaseProtocol`
- Move all params into nested `Params` struct
- Rename `call(queryParams:pathParams:expected:)` → `execute(params:completion:)`

**Step 3: Update callers**
- Update each ViewModel that calls this UseCase
- Change call site to construct `UseCase.Params(...)` and call `execute(params:completion:)`

**Step 4: Delete old Param files**
- Only after build succeeds and tests pass
- Remove from `Domain/Param/Query/` and `Domain/Param/Path/`

**Step 5: Update DI Container**
- Ensure the UseCase is registered with lazy property in module DIContainer
- See `.claude/reference/code-architecture/di-impl.md` for pattern

**Step 6: Build + test**
```bash
xcodebuild -project Talenta.xcodeproj -scheme Talenta -configuration Debug \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,arch=x86_64' \
  build CODE_SIGNING_ALLOWED=NO 2>&1 | grep -E "error:"
```

### Migrating a Repository Protocol

**Step 1: Read existing protocol**
- Identify current file location and method signatures

**Step 2: Move to `Domain/Repository/`**
- Update Xcode project references (`.xcodeproj/project.pbxproj`)
- No method signature changes unless explicitly requested

**Step 3: Build to verify**
- Ensure RepositoryImpl still compiles (it imports from Domain, so no path change needed in Swift)

## Before/After Reference

See `.claude/reference/migration.md ## UseCase Migration section` for full before/after code examples.
