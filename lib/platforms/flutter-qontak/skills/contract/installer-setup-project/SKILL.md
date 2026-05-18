---
name: installer-setup-project
description: Configure a freshly wired Flutter Qontak project for software-dev-agentic. Verifies DI wiring, route_manager setup, and symlinks. Called by installer-setup-worker.
user-invocable: false
tools: Read, Bash, Glob, Grep
---

Verify and configure a Flutter Qontak downstream project for software-dev-agentic.

## Steps

### 1 — Confirm Project Structure

**Glob** for the following key files — report any that are missing:

- `lib/engine.dart` — DI init + runApp entry point
- `lib/route_manager.dart` — `AppRouteManger` centralized router
- `lib/provider.dart` — `AppProvider` global `MultiBlocProvider`
- `lib/config/di/chat_di.dart` — `ChatDi.initDependency()` orchestrator
- `lib/config/di/main_dependency.dart` — `MainDependency` app-level registrations

### 2 — Verify DI Wiring

**Grep** `lib/config/di/chat_di.dart` for `ChatDi.initDependency` — confirm it calls:
- `CoreDependency.registerCore()`
- Feature `register*()` calls (`InboxDependency.registerInbox()`, etc.)
- `MainDependency.registerMain()` (last before notification)
- `ChatNotificationDependency.registerChatNotification()` (last)

Report any feature packages imported in `pubspec.yaml` that do not have a corresponding `register*()` call.

### 3 — Verify Route Manager

**Grep** `lib/route_manager.dart` for `AppRouteManger` — confirm it:
- Extends `RouteManager` from `chat_core`
- Has a `default:` case returning `SplashScreen`
- Has `onGenerateRoute` that wraps `getRoute` in `MaterialPageRoute`

### 4 — Verify Symlinks

**Bash** — confirm `.claude/` symlinks are wired:
```bash
ls -la .claude/agents/ | head -5
ls -la .claude/skills/ | head -5
```

If missing, tell the user to run:
```bash
software-dev-agentic/scripts/setup-symlinks.sh --platform=flutter-qontak
```

### 5 — Verify Analysis Options

**Glob** for `analysis_options.yaml` — **Grep** for `always_use_package_imports` to confirm the Mekari linter rule is active.

## Output

Report:
- Files present / missing
- DI wiring gaps (feature packages registered in pubspec but not in ChatDi)
- Route manager health
- Symlink status
- Next steps if any gaps found
