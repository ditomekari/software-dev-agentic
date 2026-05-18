---
name: installer-setup-project
description: Configure a freshly wired Flutter Qontak CRM project for software-dev-agentic. Verifies monorepo structure, DI wiring, Melos, and symlinks. Called by installer-setup-worker.
user-invocable: false
tools: Read, Bash, Glob, Grep
---

Verify and configure a Flutter Qontak CRM downstream project for software-dev-agentic.

## Steps

### 1 — Confirm Monorepo Structure

**Glob** for the following key files — report any that are missing:

- `melos.yaml` — Melos monorepo config
- `pubspec.yaml` — root app pubspec
- `lib/engine.dart` — initialization entry point (Firebase → ObjectBox → DI → runApp)
- `lib/configs/di/crm_di.dart` — `CrmDi` DI orchestrator
- `lib/configs/di/qontak_crm_dependency.dart` — app-level GetIt registrations
- `lib/configs/modules.dart` — `featureModules` list
- `features/` — feature packages directory

### 2 — Verify DI Wiring

**Read** `lib/configs/di/crm_di.dart` — confirm it:
- Registers `QontakCommonDependency` first and awaits `allReady()`
- Registers `QontakCoreDependency` next
- Registers all feature `Qontak<Feature>Dependency.register<Feature>()` calls
- Report any feature packages in `melos.yaml` that do not have a corresponding `register*()` call

### 3 — Verify Feature Package Structure

For one sample feature (e.g. `features/crm_company/`):
**Glob** to confirm `lib/src/` has subdirs: `config/`, `data/`, `domain/`, `presentation/`

### 4 — Verify Symlinks

**Bash** — confirm `.claude/` symlinks are wired:
```bash
ls -la .claude/agents/ | head -5
ls -la .claude/skills/ | head -5
```

If missing, tell the user to run:
```bash
software-dev-agentic/scripts/setup-symlinks.sh --platform=flutter-qontak-crm
```

### 5 — Verify Analysis Options

**Glob** for `analysis_options.yaml` at repo root — **Grep** for `always_use_package_imports` to confirm the Mekari linter rule is active.

### 6 — Verify Melos Bootstrap

**Bash**:
```bash
cat melos.yaml | grep -E 'packages|scripts'
```

Confirm feature packages are listed under `packages:` and that `bootstrap` or `get` scripts are defined.

## Output

Report:
- Files present / missing
- DI wiring gaps
- Feature package structure health
- Symlink status
- Melos configuration status
- Next steps if any gaps found
