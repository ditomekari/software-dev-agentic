> Related: Core Design Principles · Shared Agentic Submodule Architecture

## What is the Builder Persona?

The **builder** persona is the primary feature-building workflow. It handles the full CLEAN Architecture build cycle — from domain layer through presentation — across all platforms.

Location: `lib/core/agents/builder/`

---

## Anatomy

The builder persona has three entry skills. All use the same orchestrator brain and the same convergence planning loop — they differ only in how intent is gathered and how blocking decisions are handled.

```
User
 │
 ├─ /builder-plan-feature          — interactive; convergence loop + user approval + worker
 ├─ /builder-build-feature         — direct entry; routes resume vs new, or build-directly
 └─ /builder-build-from-ticket     — non-interactive; derives intent from Jira ticket, auto-approves
          │
          │  Step 1: gather-intent (or gather-intent-prefilled for ticket path)
          ▼
    builder-feature-orchestrator   — brain only; returns Decision blocks; never spawns or writes
          │
          │  Decision: spawn-planners (which layers, why)
          ▼
    Entry skill spawns planners in parallel (only those decided by orchestrator)
          │
          ├─ builder-domain-planner    — Domain: entities, use cases, repository interfaces
          ├─ builder-data-planner      — Data: DTOs, mappers, datasources, repo implementations
          ├─ builder-pres-planner      — Presentation: StateHolders, screens, key symbols
          └─ builder-app-planner       — App: DI registration, routing, module registration
          │
          │  Planners return findings + Impact Recommendations
          ▼
    Entry skill sends accumulated findings to orchestrator
          │
          │  Decision: converged / spawn-planners (next round) / blocked
          ▼
    Loop continues until converged (max 3 rounds)
          │
          │  Decision: converged → orchestrator synthesizes plan.md + context.md
          │
          │  [interactive path: user reviews and approves plan.md]
          │  [ticket path: auto-approved]
          │
          │  Decision: spawn-worker
          ▼
    builder-feature-worker         — reads approved plan; executes skills in layer order
          │
          ▼
    platform-contract skills       — concrete artifact creation per platform and layer
```

---

## Entry Skills

| Skill | When to use | Difference |
|---|---|---|
| `/builder-plan-feature` | Complex or cross-layer features; uncertain existing state | Interactive convergence loop; user reviews plan before execution |
| `/builder-build-feature` | Known scope; resuming an existing run; or build-directly opt-out | Routes resume vs new; build-directly skips the loop |
| `/builder-build-from-ticket` | CI job, API caller, automated pipeline | Non-interactive; intent derived from Jira ticket; auto-approves |

---

## Planning Convergence Loop

The entry skill (not the orchestrator) owns the loop. Each round:

1. Orchestrator decides which planners are needed based on intent and prior findings
2. Entry skill spawns only those planners in parallel
3. Planners return findings + `### Impact Recommendations` (which other layers are affected)
4. Entry skill sends accumulated findings to orchestrator
5. Orchestrator checks: are all required recommendations covered by the visited set?
   - No → `Decision: spawn-planners` for the next round (unvisited layers only)
   - Yes → `Decision: converged`

**Guards:**
- Visited set prevents re-spawning already-explored layers
- Hard cap at 3 rounds → `Decision: blocked` surfaces to user (or `error.md` for ticket path)

---

## Orchestrator Modes

`builder-feature-orchestrator` is called multiple times per feature build, each time in a different mode:

| Mode | Called when | Returns |
|---|---|---|
| `gather-intent` | New interactive feature | `Decision: spawn-planners` (round 1) |
| `gather-intent-prefilled` | Ticket path; intent pre-derived | `Decision: spawn-planners` (round 1) |
| `process-findings` | After each planner round | `Decision: spawn-planners` / `Decision: converged` / `Decision: blocked` |
| `synthesize` | After convergence; skill passes all findings | Writes `plan.md` + `context.md`; returns summary |

---

## Sub-Planners

Each planner explores one layer, reports findings, and returns. Spawned by the entry skill in parallel per round.

| Planner | Explores | Impact Recommendations |
|---|---|---|
| `builder-domain-planner` | Entities, use cases, repository interfaces, domain services | → data (new entity needs DTO), → app (new use case needs DI) |
| `builder-data-planner` | DTOs, mappers, datasources, repository implementations | → domain (contract gap), → app (new impl needs DI binding) |
| `builder-pres-planner` | StateHolders, screens, components, navigators, key symbols | → domain (missing use case), → app (new screen needs route) |
| `builder-app-planner` | DI registration, routing, module registration, analytics, feature flags | → domain / presentation (flag or route impacts) |

### Scope-Aware Entry

The orchestrator passes a `scope` map in every `spawn-planners` decision block. Each planner uses its scope to skip glob steps for artifact types not relevant to the stated intent — so a "update use case" task causes the domain planner to only search for use cases, not entities, repository interfaces, or services.

### Demand-Driven Reference Expansion

After reading primary artifact symbols, each planner checks its referenced types and expands **only if**:

- **(a) Structural need** — the referenced type's shape is required to describe the new/modified artifact (e.g. a use case returns `UserEntity` and its fields must be listed in the findings), **or**
- **(b) Modification need** — the referenced type itself will be modified as a consequence of the change (e.g. adding a use case output field requires a new entity property)

All other referenced types — injected dependencies, pass-throughs, unrelated artifacts — are skipped. The decision stays inside the planner; the orchestrator only controls the entry point via `scope`.

---

## Execution Phase — `builder-feature-worker`

`builder-feature-worker` is the only agent that writes source files. It reads the approved `plan.md` and calls skills in CLEAN layer order — domain → data → presentation → UI. Each artifact is validated via `Glob` + `Grep` before moving to the next. `state.json` is updated after each artifact so the run is resumable.

---

## Agent Roster

### Core agents (`lib/core/agents/builder/`)

| Role | Agent | Responsibility |
|---|---|---|
| Orchestrator | `builder-feature-orchestrator` | Brain of the builder persona — decides which planners, synthesizes plan, instructs skill to spawn worker |
| Orchestrator | `builder-groom-orchestrator` | Grooming brain — detects scope from AC, decides which planners, synthesizes grooming summary |
| Orchestrator | `builder-backend-orchestrator` | Backend API + data layer coordination |
| Planner | `builder-domain-planner` | Domain layer exploration — entities, use cases, repository interfaces |
| Planner | `builder-data-planner` | Data layer exploration — DTOs, mappers, datasources, repo implementations |
| Planner | `builder-pres-planner` | Presentation layer exploration — StateHolders, screens, key symbols |
| Planner | `builder-app-planner` | App layer exploration — DI, routing, module registration, analytics, feature flags |
| Worker | `builder-feature-worker` | Plan-driven executor — reads plan.md, calls skills in layer order, validates each artifact |
| Worker | `builder-test-worker` | Test generation across all layers |
| Worker | `auditor-arch-review-worker` | CLEAN Architecture violation review (downstream projects) |

**Deprecated (absorbed into orchestrator + entry skills):**

| Agent | Replaced by |
|---|---|
| `builder-feature-planner` | `builder-feature-orchestrator` (synthesize mode) + entry skill (convergence loop) |
| `builder-auto-feature-planner` | `builder-feature-orchestrator` (gather-intent-prefilled mode) + `builder-build-from-ticket` skill |

**Removed:**

| Agent | Removed in | Reason |
|---|---|---|
| `domain-worker` | v3.58.0 | Superseded by `builder-feature-worker` and `builder-backend-orchestrator` |
| `data-worker` | v3.58.0 | Superseded by `builder-feature-worker` and `builder-backend-orchestrator` |
| `presentation-worker` | v3.58.0 | Superseded by `builder-feature-worker` |
| `builder-ui-worker` | v5.6.0 | No valid spawn path — violated Skill-First Entry; Component Reuse Check merged into `builder-feature-worker` |

### Platform agents

| Platform | Agent | Why platform-specific |
|---|---|---|
| iOS | `test-orchestrator` | Knows `xcodebuild`, XCTest flow |
| iOS | `pr-review-worker` | Knows Swift/UIKit conventions |

### Internal tooling (NOT symlinked downstream)

| Component | Location | Purpose |
|---|---|---|
| `arch-review-orchestrator`, `arch-review-worker` | `.claude/agents/` | Convention review |
| `arch-check-conventions`, `arch-generate-report` | `.claude/skills/` | Convention checklist, report formatter |

---

## Layer-to-Agent Mapping

| Layer | Planner | Worker | Skills |
|---|---|---|---|
| Domain | `builder-domain-planner` | `builder-feature-worker` | `builder-domain-create-entity`, `builder-domain-create-usecase`, `builder-domain-create-repository`, `builder-domain-create-service` |
| Data | `builder-data-planner` | `builder-feature-worker` | `builder-data-create-datasource`, `builder-data-create-mapper`, `builder-data-create-repository-impl` |
| Presentation | `builder-pres-planner` | `builder-feature-worker` | `builder-pres-create-stateholder`, `builder-pres-create-screen`, `builder-pres-create-component` |
| App | `builder-app-planner` | `builder-feature-worker` (inline) | — |
| Test | — | `builder-test-worker` | `builder-test-create-domain`, `builder-test-create-data`, `builder-test-create-presentation` |

---

## Skill Roster (Platform-Contract — all platforms must implement)

These skills cover **artifact creation only**. Workers handle modifications to existing artifacts via direct `Read` + `Edit` with reference docs — there are no `update-*` or `fix-*` skills.

| Skill | Called by | Layer |
|---|---|---|
| `builder-domain-create-entity` | `builder-feature-worker` | Domain |
| `builder-domain-create-repository` | `builder-feature-worker` | Domain |
| `builder-domain-create-usecase` | `builder-feature-worker` | Domain |
| `builder-domain-create-service` | `builder-feature-worker` | Domain |
| `builder-data-create-mapper` | `builder-feature-worker` | Data |
| `builder-data-create-datasource` | `builder-feature-worker` | Data |
| `builder-data-create-repository-impl` | `builder-feature-worker` | Data |
| `builder-pres-create-stateholder` | `builder-feature-worker` | Presentation |
| `builder-pres-create-screen` | `builder-feature-worker` | Presentation/UI |
| `builder-test-create-domain` | `builder-test-worker` | Test |
| `builder-test-create-data` | `builder-test-worker` | Test |
| `builder-test-create-presentation` | `builder-test-worker` | Test |

---

## Standalone Paths (no convergence loop needed)

| Task | Path |
|---|---|
| Single known artifact | Entry skill (`/builder-build-feature`) with narrow intent → orchestrator scopes to one layer → `builder-feature-worker` |
| Test generation | `builder-test-worker` directly |
| Targeted edit to existing artifact | Worker with `context.md` Key Symbols if available |

---

## Agent Count Snapshot

| Category | `lib/core/agents/` | `lib/platforms/ios/agents/` | `lib/platforms/web/agents/` |
|---|---|---|---|
| Orchestrators | 3 in `builder/` + 1 in `detective/` | 1 (`test-orchestrator`) | — |
| Workers | 2 in `builder/` + 2 in `detective/` + 1 in `tracker/` + 1 in `auditor/` + 1 in `installer/` | 1 (`pr-review-worker`) | — |
| Skills (Type A) | — | 29 | 29 |
| Skills (Type B) | — | 2 | 0 |

> This is a point-in-time snapshot. Check `lib/core/agents/` and `lib/platforms/` for the current roster.

---

## Execution Examples

### Builder flows

**Direct action** — "Add import RxSwift to this file" → single-line edit, no agent needed

**Single-layer task** — "Create GetLeaveRequestListUseCase"
→ `/builder-build-feature` with narrow intent; orchestrator scopes to domain only; `builder-feature-worker` calls `builder-domain-create-usecase`

**Multi-layer task** — "Build the leave request feature"
→ `/builder-plan-feature` skill: orchestrator decides which planners, skill runs convergence loop, plan approved, `builder-feature-worker` executes

**Partial update** — "Add a new screen, domain/data already exist"
→ orchestrator decides: spawn only `pres-planner` + `app-planner` (domain and data have no impact)

**Cross-layer impact discovered** — pres-planner reports "new screen needs a use case that doesn't exist"
→ orchestrator spawns domain-planner in round 2 to explore; skill adds `domain` to visited set

**Type B skill** — `/migrate-presentation CustomFormScreen`
→ explicit user trigger; prevents accidental migration

**Ticket-driven build** — `/builder-build-from-ticket PROJ-123`
→ skill derives intent from ticket, runs convergence loop automatically, auto-approves, executes worker

**Flutter domain entity creation** — "Create a LeaveRequest entity for Flutter"

```
/builder-plan-feature skill
  └─ builder-feature-orchestrator   (decides: spawn domain-planner only)
  └─ builder-domain-planner         (explores domain layer)
  └─ builder-feature-orchestrator   (converged; synthesizes plan.md)
  └─ builder-feature-worker         (reads plan; calls skill)
        └─ builder-domain-create-entity   ← flutter skill, knows the syntax
```

**iOS PR review** — "Review my PR before merging"

```
pr-review-worker       (iOS platform worker)   ← iOS-specific workflow
  └─ review-pr         (iOS platform skill)    ← Swift/UIKit conventions
       lib/platforms/ios/skills/review-pr/SKILL.md
```

### Other persona flows

**Debug flow** *(detective)* — "Why is form submission silently failing?"
→ `detective-debug-orchestrator` gathers context, spawns `detective-debug-worker`

**Agent prompt debugging** *(detective)* — "Why did the worker create an implementation instead of an interface?"

```
perf-worker           ← scores session D1–D7
  D2: 5/10            ← worker invocation anomaly flagged
  → surfaces ambiguous "create the repository" instruction
  → suggests rewrite with explicit scope
```

**Convention audit** *(auditor)* — "Run arch-review-orchestrator for lib/core"
→ spawns workers per scope; `arch-generate-report` formats findings

**Project setup** *(installer)* — "Set up this project with the starter kit"
→ `installer-setup-worker` detects platform, runs `setup-nextjs-project` or `setup-ios-project` skill, provides orientation

---

## Implementation Reference

| Project | Stack | Status |
|---|---|---|
| talenta-ios | Swift/UIKit, 4 orchestrators, 7 workers, 27 skills | Content mirrored in `lib/platforms/ios/`. Still uses its own copy — submodule wiring pending. |
| mobile-talenta (Flutter) | Dart/BLoC, get_it + injectable DI, 7 agents, 9 skills | `lib/platforms/flutter/` is a stub — needs agents, skills, reference docs |
| talenta-mobile-android | Kotlin MVP, Dagger 2, RxJava 3 | `lib/platforms/android/` scaffolded — 12 contract skills, 6 reference docs. Wire submodule with `setup-symlinks.sh --platform=android`. |
| wehire, xpnsio | Next.js 15, 29 Type A skills, 0 Type B | Active — consuming submodule via web platform |

> **Breaking:** downstream projects must re-run setup scripts after updating the submodule pointer.

---

## Open Items

| # | Topic | Status |
|---|---|---|
| 1 | Migration: talenta-ios | Agents/skills/reference content copied to `lib/platforms/ios/`. Full submodule wiring = separate session. |
| 2 | Versioning | ✅ Resolved — semantic versioning established: v2.0.0 tagged. |
| 3 | Naming alignment | Flutter/Android adopt `-orchestrator` / `-worker` suffix — required before migration |
| 4 | Reference doc splitting | Structural split of `lib/platforms/web/reference/code-architecture/data.md` and `lib/platforms/web/reference/utilities.md` by operation type |
| 5 | Flutter implementation | `lib/platforms/flutter/` is a stub — needs agents, skills, reference docs |

---

## CLEAN Architecture, SOLID, and DRY

> Layer-to-agent mapping: see [Layer-to-Agent Mapping](#layer-to-agent-mapping) above.

**SOLID via Agent Design:**
- **SRP:** Each worker handles exactly one layer; each skill does exactly one task; orchestrator only reasons and decides
- **OCP:** New features add new agents/skills without modifying existing ones
- **DIP:** Workers define the protocol; platform skills are the implementations
- **DRY via Architecture:** Reference docs are the single source of truth — skills Grep section pointers, never embed content.

---

## Delegation Threshold

Always use the convergence planning loop when a task touches more than 3 architectural layers — inline execution at that scope produces inconsistent results.

> Rule: if the task takes fewer tokens to DO than to DELEGATE, do it directly. Otherwise, delegate.
