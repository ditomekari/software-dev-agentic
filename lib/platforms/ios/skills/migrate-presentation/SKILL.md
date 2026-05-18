---
name: migrate-presentation
description: |
  Migrate Presentation layer components to V2 architecture: old custom StateHolder *(iOS: ViewModel)* → BaseViewModelV2 with State/Event/Action, add Navigator protocol + Coordinator, wire into DI Container. One StateHolder per run.
user-invocable: true
---

# Migrate StateHolder *(iOS: ViewModel)* to V2

Migrate one Presentation layer component at a time to the modern architecture standard.

## Architecture Reference

Read these before starting:
- `.claude/reference/code-architecture/presentation-impl.md` — V2 ViewModel, State/Event/Action, Navigator, Coordinator
- `.claude/reference/code-architecture/presentation-impl.md #Advanced-Patterns` — Navigator protocol pattern, Coordinator pattern
- `.claude/reference/migration.md ## Legacy Code Migration Checklist section` — legacy code migration checklist
- `.claude/reference/code-architecture/di-impl.md` — factory method pattern in DIContainer

## Scope

This skill covers **Presentation layer only**:
- ViewModel: old custom ViewModel → `BaseViewModelV2` with `State`, `Event`, `Action` types
- Navigator protocol + Coordinator (if navigation logic is inline in ViewController)
- DI wiring: factory method in module DIContainer

**Out of scope for this skill:** UseCases, Repositories, Mappers (use `/migrate-usecase`). ViewController UI code is not changed unless the user explicitly asks.

## Safety Rules

⚠️ **BEFORE touching any file:**
1. Read the file — identify its current pattern (V1 legacy or V2 modern)
2. If already V2 — do nothing, report to user
3. Migrate **one ViewModel per run**
4. Keep existing RxSwift bindings intact — only restructure the State/Event/Action wrapper
5. Run build after each file change before proceeding to the next
6. Never rename public-facing outputs (Observables, Drivers) that ViewControllers already bind to without user confirmation
7. Don't migrate ViewController unless user explicitly asks

## What to Ask First

Before starting, ask the user:
1. Which ViewModel to migrate?
2. Is there an existing test file? (tests must stay green — update them if needed)
3. Does this ViewModel have navigation logic? (need to extract Navigator if so)
4. Is the module DIContainer already set up?

## Implementation Steps

### Migrating a ViewModel to BaseViewModelV2

**Step 1: Read the existing ViewModel**
- Note all inputs (methods/subjects the ViewController calls)
- Note all outputs (Observables/Drivers the ViewController binds)
- Note all UseCase dependencies
- Note any navigation calls

**Step 2: Define State, Event, Action**
```swift
// State: what the UI renders
struct State { ... }

// Event: one-time UI notifications (show toast, show error)
enum Event { ... }

// Action: what the user does
enum Action { ... }
```

**Step 3: Rewrite ViewModel**
- Extend `BaseViewModelV2<State, Event, Action>`
- Move UseCase calls into `handle(action:)` or `transform()`
- Replace ad-hoc subjects with `state`, `event` relays from base class

**Step 4: Extract Navigator (if navigation logic exists)**
- Create `[Feature]Navigator` protocol with `weak var` delegate
- Move navigation calls from ViewModel to Navigator
- See `.claude/reference/code-architecture/presentation-impl.md #Navigator-Protocol-Pattern`

**Step 5: Update ViewController bindings**
- Update any call sites that changed (inputs → `send(action:)`, outputs → `state.map { ... }`)
- Existing Driver bindings usually need minimal change

**Step 6: Update or create tests**
- ViewModel tests: use `state` relay assertions instead of direct property checks
- See `.claude/reference/code-architecture/testing-impl.md` for test patterns

**Step 7: Wire DI Container**
- Add factory method: `func make[Feature]ViewModel(navigator: [Feature]Navigator) -> [Feature]ViewModel`
- See `.claude/reference/code-architecture/di-impl.md`

**Step 8: Build + test**
```bash
xcodebuild -project Talenta.xcodeproj -scheme Talenta -configuration Debug \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,arch=x86_64' \
  build CODE_SIGNING_ALLOWED=NO 2>&1 | grep -E "error:"
```

## Before/After Reference

See `.claude/reference/code-architecture/presentation-impl.md` for full V2 ViewModel pattern.
See `.claude/reference/migration.md ## Legacy Code Migration Checklist section` for legacy code migration checklist.
