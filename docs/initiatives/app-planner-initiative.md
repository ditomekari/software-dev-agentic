# App-Planner Initiative

**Status:** Planning
**Goal:** Extend the builder persona to cover app-layer wiring — DI registration, route registration, and module registration — which currently has no planner and falls through as unplanned work.

---

## Problem

The current planning system covers exactly three CLEAN layers: domain, data, presentation. Any feature also requires wiring into the app shell:
- DI container — register use cases, repositories, data sources
- Route registration — add routes/destinations/coordinators
- Module registration — plug the feature into the app's module system

This work currently has no planner. It either falls to `feature-worker` to handle inline (no human gate, no layer validation) or is missed entirely.

---

## Solution

Add an `app-planner` agent to `lib/core/agents/builder/` that explores app-layer wiring patterns for a feature. `feature-planner` spawns it in parallel alongside `domain-planner`, `data-planner`, and `pres-planner`. Its findings land in a new `## App Layer` section in `plan.md`.

---

## Canonical Headings (Ubiquitous Language)

These three headings apply across all platforms. Same heading text, platform-specific body.

| Heading | What it covers |
|---|---|
| `## Dependency Registration` | How use cases, repositories, data sources are bound to the DI container |
| `## Route Registration` | How screens, destinations, or routes are declared for navigation |
| `## Module Registration` | How a feature module is wired into the app's module system |

---

## Platform Findings

### iOS (talenta-ios)

| Heading | Pattern | Key Files |
|---|---|---|
| Dependency Registration | Needle `Component<DependencyType>` — hierarchical component tree | `Talenta/DIComponents/RootComponent.swift`, `MainTabComponent.swift`, `NeedleGenerated.swift` |
| Route Registration | Coordinator pattern — `BaseCoordinator<ResultType>` with Rx lifecycle | `Talenta/Base/BaseCoordinator.swift`, `Talenta/Controllers/{Feature}/*Coordinator.swift`, `Talenta/DIComponents/DeeplinkComponent.swift` |
| Module Registration | Needle component hierarchy (implicit — child components of `MainTabComponent`) | `Talenta/DIComponents/MainTab/{Feature}/` |

### Flutter (mobile-talenta)

| Heading | Pattern | Key Files |
|---|---|---|
| Dependency Registration | `get_it` service locator + `@injectable` code generation per feature | `lib/src/configs/di/talenta_dependencies.dart`, `talenta/lib/src/features/{feature}/configs/di/{feature}_dependencies.dart` |
| Route Registration | Named routes + route factory per feature (`getPageByName` + `getListProviderByName`) | `talenta/lib/src/features/{feature}/utils/navigation/{feature}_route.dart`, `{feature}_route_factory.dart` |
| Module Registration | `BaseModule` implementation + registration in `TalentaModuleManager` | `talenta/lib/src/features/{feature}/{feature}.dart`, `talenta/lib/src/shared/core/module/module_manager.dart` |

### Android (talenta-mobile-android) — for future platform addition

| Heading | Pattern | Key Files |
|---|---|---|
| Dependency Registration | Dagger 2 `@Module` + `@Binds` + `@ContributesAndroidInjector` per feature | `app/src/main/java/co/talenta/di/MainComponent.kt`, `feature_*/di/Feature*Module.kt`, `*ActivityBindingModule.kt` |
| Route Registration | Interface-based navigation — interface in `base/`, impl in `app/navigator/`, bound in `NavigationModule` | `base/navigation/{Feature}Navigation.kt`, `app/navigator/{Feature}NavigationImpl.kt`, `app/di/NavigationModule.kt` |
| Module Registration | `*ActivityBindingModule` added to `MainComponent` modules list + Gradle `include` in `settings.gradle` | `app/di/MainComponent.kt`, `settings.gradle`, `app/build.gradle` |

---

## Files to Create

### 1. Core Reference Doc

**`lib/core/reference/code-architecture/app-layer.md`**

Defines what each concept IS — platform-agnostic theory.

Sections (with `<!-- N -->` line counts):
- `## Dependency Registration` — what DI registration is; why it's separate from CLEAN layers; what belongs here vs domain/data layer
- `## Route Registration` — what route registration is; coordinator vs named route vs nav graph
- `## Module Registration` — what module registration is; when it applies; distinction from DI

---

### 2. iOS Platform Contract Reference Doc

**`lib/platforms/ios/reference/contract/builder/app-layer.md`**

Sections:
- `## Dependency Registration` — Needle Component pattern; how to create a child component; how `RootComponent` / `MainTabComponent` hierarchy works; where to add new component
- `## Route Registration` — Coordinator pattern; `BaseCoordinator<ResultType>`; how to create a feature coordinator; how to wire into `DeeplinkComponent`
- `## Module Registration` — Needle component hierarchy; how to register a new child component under `MainTabComponent`

---

### 3. Flutter Platform Contract Reference Doc

**`lib/platforms/flutter/reference/contract/builder/app-layer.md`**

Sections:
- `## Dependency Registration` — get_it + injectable pattern; `{feature}_dependencies.dart` structure; `@injectable` annotation on BLoCs; how to add a new feature DI file
- `## Route Registration` — `{feature}_route.dart` (constants) + `{feature}_route_factory.dart` (page + provider factories); `BaseModule.getPageByName` / `getProvidersByName` contract
- `## Module Registration` — `BaseModule` implementation; how to register in `TalentaModuleManager`

---

### 4. App-Planner Agent

**`lib/core/agents/builder/app-planner.md`**

Frontmatter:
```
name: app-planner
description: Explore app-layer wiring for a given feature — discovers existing DI registration, route registration, and module registration patterns. Returns structured findings for feature-planner to synthesize. No writes.
model: sonnet
tools: Glob, Grep, Read
```

Structure mirrors `domain-planner.md`:
- `## Input` — `feature`, `platform`, `module-path`
- `## Search Protocol` — Grep-first, Read with offset+limit
- `## Workflow`
  - Step 1 — Load platform app-layer reference (`reference/contract/builder/app-layer.md`)
  - Step 2 — Locate DI container files for this platform
  - Step 3 — Locate routing/navigation files
  - Step 4 — Locate module registration files (if applicable)
  - Step 5 — Detect patterns from existing entries
- `## Output` — `## App Findings` with three subsections: Dependency Registration, Route Registration, Module Registration
- `## Extension Point`

---

### 5. Updates to Existing Files

**`lib/core/agents/builder/feature-planner.md`**

Phase 2 — spawn `app-planner` alongside the three layer planners (four in parallel).

Phase 3 — aggregate `## App Findings` into plan.md.

**plan.md format** — add `## App Layer` section after `## Presentation Layer`:

```markdown
## App Layer

| Concern | File | Action | Notes |
|---|---|---|---|
| Dependency Registration | `path/to/di-container` | update | add LoginUseCase, AuthRepository |
| Route Registration | `path/to/router` | update | add /login route |
| Module Registration | `path/to/module-manager` | update | register AuthModule |
```

**`lib/core/agents/builder/feature-worker.md`**

Add App Layer step after Presentation Layer execution:
- Read `plan.md` App Layer section
- For each entry: Read the target file → Edit to add the new wiring
- Validate: Grep for the new entry in the modified file
- No skill needed — app-layer wiring is always modifying existing files via direct Read + Edit

---

## Execution Order

1. Write `lib/core/reference/code-architecture/app-layer.md` (core theory)
2. Write `lib/platforms/ios/reference/contract/builder/app-layer.md`
3. Write `lib/platforms/flutter/reference/contract/builder/app-layer.md`
4. Write `lib/core/agents/builder/app-planner.md`
5. Update `lib/core/agents/builder/feature-planner.md` — add app-planner to Phase 2 spawn + Phase 3 aggregation
6. Update plan.md format in feature-planner (Phase 4 — Write plan.md)
7. Update `lib/core/agents/builder/feature-worker.md` — add App Layer execution step
8. Update `docs/principles/core-design-principles.md` — Layer Isolation section now correctly references app-planner alongside the three layer planners
9. Commit + release

## Open Questions

- **web platform**: Next.js App Router uses file-based routing — no explicit route registration. DI container may vary by project. Defer web app-layer reference doc until a concrete web project pattern is confirmed.
- **Android platform**: Not yet a submodule platform. Android app-layer findings documented here for when Android is added.
