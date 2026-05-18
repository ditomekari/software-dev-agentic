> Author: Puras Handharmahua · 2026-04-08
> Related: Shared Agentic Submodule Architecture — Cross-Platform Scaling

## What is an Agentic Coding Assistant?

A coding assistant where Claude autonomously routes, decides, and executes — without the user needing to know which tool, command, or workflow to invoke. Trigger skills are the only supported entry path: they own routing, context relay, and spawn prompt construction.

> Skills first. No manual chaining. No context pollution.

**Current scope:** This system today covers the **Implementation** process of the SDLC (build, debug, review, groom). The long-term goal is specialized agents across every process — Requirement, Design, Implementation, Testing, and Delivery. Expansion into other processes depends on the Collaboration and Distribution phases being resolved first.

---

## Design Goals

1. **Consistent agentics across platforms** — same agents, same principles, one source of truth
2. **Easy to maintain** — update once, all projects get it
3. **Open contribution model** — all engineers can explore, create, and PR new agents/skills
4. **Context efficiency** — no wasted tokens on irrelevant content
5. **Encouraging initiatives** — low barrier to propose new "personas" (orchestrators)

---

## Core Design Principles

### 1. Skill-First Entry

**Trigger skills are the only supported entry path.** A Type W skill owns the full entry sequence before any agent is spawned: routing (resume vs new run), context pre-loading from the runs directory, and building the spawn prompt with context already inlined. This eliminates cold pre-flight reads, gives the user clear options, and keeps orchestration efficient.

> Not every request needs an agent. If a change is simple and localized (rename a variable, fix a typo, add an import), act directly — the cost of delegation exceeds the task itself.

**Skill-First Entry for Personas:**

Every persona must have exactly one primary entry agent. That agent must have a corresponding Type W workflow skill. The skill is the only supported entry path — direct agent invocation bypasses context loading and is unsupported.

| Role | Has trigger skill? | Spawned by |
|---|---|---|
| Persona entry agent (orchestrator, or single worker if no orchestrator) | Yes — required | User via trigger skill |
| Workers inside a persona | No | Orchestrator only |

The trigger skill owns three responsibilities before spawning the agent:
1. **Routing** — detect existing runs (resume vs new call) and ask the user when ambiguous
2. **Context pre-loading** — read `plan.md`, `context.md`, and `state.json` from the runs directory and inline them into the spawn prompt
3. **Spawn prompt construction** — pass the pre-loaded block so the agent can skip all cold pre-flight file reads

The agent detects the `Pre-loaded context` block in its prompt and jumps directly to the first pending phase. Without it, the agent warns that direct invocation is unsupported.

**Multiple workflow skills per persona are allowed** — as long as they all route through the same primary entry agent. Example: the builder persona has three Type W skills: `builder-build-feature` (direct build or resume), `builder-plan-feature` (planning-first workflow that runs a convergence planning loop → user approval → `feature-worker`), and `builder-build-from-ticket` (non-interactive CI/remote path — fetches a Jira ticket, runs the planning loop automatically, then `feature-worker` without any user prompts). All converge on the same executor; the rule guards against direct-invocation bypasses, not workflow variations.

A sub-agent used only as a step inside a workflow skill (e.g. `feature-planner` inside `builder-plan-feature`) does not need its own standalone trigger skill.

> **Adding a new persona:** create the entry agent + its trigger skill together. A persona without a trigger skill is incomplete.

---

### 2. Agents = Brain (Decision-Maker)

Agents are intelligent specialists, not task executors. Each agent:

- Assesses context before acting (does this file exist? which pattern applies?)
- Decides which procedure to execute
- Handles edge cases and branching logic
- Knows *what* to do and *when*

Agents stay lean — they don't embed step-by-step instructions. That belongs in skills.

**Orchestrators — Brain-Only Decision Makers:**

Orchestrators are pure reasoning agents — they decide what to do and return structured decision blocks to the calling skill. The skill executes: it spawns agents, accumulates results, and loops. Key rules:

- Return structured decision blocks (`Decision: spawn-planners`, `Decision: converged`, `Decision: spawn-worker`, `Decision: blocked`) — never spawn agents directly
- Never write or edit files — all writes go through workers spawned by the skill
- Pass file paths between phases, never file contents
- Never read codebase source files directly — planners and workers own their own context reads

**Agent Scope — Core vs Platform-specific:**

Agents have a second axis — where they live and what they know.

- **Core** (`lib/core/agents/`) — platform-agnostic. Work on any platform. Add here when the behaviour is identical across all platforms.
- **Platform-specific** (`lib/platforms/<platform>/agents/`) — exist only when the workflow diverges enough from core to need its own agent. Examples: iOS `test-orchestrator` (knows `xcodebuild`), iOS `pr-review-worker` (knows Swift/UIKit conventions). Do not add a platform agent unless a core agent + platform skills cannot handle it.

> For the full agent roster, see [persona-builder.md](persona/builder.md).

**DI at Skill Level:**

Workers are platform-agnostic protocol-definers. Skills are the platform-specific implementations of that protocol. A `domain-worker` calls `builder-domain-create-entity` by name — on iOS that creates a Swift struct, on web a TypeScript interface. The worker never knows which platform it's on and doesn't need to.

**Skills are create-only.** Platform-contract skills cover new artifact creation only (`create-*`). There are no update or fix skills — workers handle modifications to existing artifacts via direct `Read` + `Edit` with reference docs. Workers invoke a skill only when the target artifact does not yet exist.

| Role | Protocol analogy | Platform-aware? |
|---|---|---|
| Orchestrators | Interface contract | No |
| Planners | Requirements analysis | No |
| Workers | Use-case logic | No |
| Skills | Concrete implementation | Yes |

**Layer Isolation — Bounded Knowledge and Authority:**

Layer isolation is enforced at the **planner** level, not the worker level. `feature-worker` is a single executor that handles all CLEAN layers sequentially, guided by `plan.md`. The planners are what are layer-bounded:

- Each layer planner (`domain-planner`, `data-planner`, `pres-planner`, `app-planner`) is restricted to read-only tools (`Glob`, `Grep`, `Read`) — it physically cannot write files
- Each planner's glob patterns and instructions scope it to its own layer's directories and artifact types
- Cross-layer knowledge (shared contracts, interfaces) lives in reference docs and skills, not in planner bodies
- Planners report `### Impact Recommendations` — which other layers their findings affect and why. The orchestrator uses these to decide whether additional planner rounds are needed

The calling skill (not the orchestrator) spawns planners based on the orchestrator's decision. This convergence loop continues until all impact recommendations are resolved or the round cap is reached.

`feature-worker` executes all layers in a fixed order (domain → data → presentation → UI) using skills as the platform-specific hands. Layer correctness in the worker comes from following `plan.md` and calling the right skill per artifact type — not from a boundary enforcement mechanism.

**Context Isolation = Efficiency:**

Every agent runs in its own isolated context window — completely separate from the main session. This is the primary mechanism for token efficiency.

From the official docs:
> *"Preserve context by keeping exploration and implementation out of your main conversation"*

When a worker reads reference docs, scans existing files, and writes code — none of that touches your main session context. The main session only sees the result.

| Component | Context cost | Mechanism |
|---|---|---|
| Core agents (descriptions) | ~3–5 lines each in main session | Agent tool definition |
| Platform-specific agents (descriptions) | ~3–5 lines each in main session | Agent tool definition |
| Preloaded skills | Loaded at worker startup only | `skills` field |
| Reference docs | 1 Grep call per section needed | Grep-first in worker body |
| `agents.local/extensions/` | 1 Read call (conditional) | Extension hook in shared agent |
| Dead weight (unselected groups) | Zero | Persona groups not linked if not selected |
| Orchestrator context accumulation | Minimal — file paths only | Workers return paths, not content; state file prevents re-reads |
| Context relay (trigger skills) | Zero pre-flight reads in the spawned agent | Skill reads `plan.md`, `context.md`, and `state.json` from the runs directory on disk, inlines all three into the spawn prompt; orchestrator detects the pre-loaded block and skips pre-flight file reads entirely |

**Context relay pattern:**

When a trigger skill spawns an orchestrator on resume, it reads `plan.md`, `context.md`, and `state.json` from `.claude/agentic-state/runs/<feature>/` and inlines their contents directly into the spawn prompt. The orchestrator receives context on its first token and jumps directly to the next pending phase — it never reads those files itself.

This works in both same-session and new-session resumes — the files are on disk, so the trigger skill always reads them regardless of cache state. The spawned agent pays zero pre-flight read cost in either case. Disk is the authoritative source; the trigger skill is the bridge.

**Fail-Fast Precondition Validation:**

Agents validate preconditions before executing procedures — they never guess or proceed with assumptions.

**Workers check on entry (`## Input`):**
- Are all required spawn parameters present? — return `MISSING INPUT: <param>` immediately if not
- Is the task within this worker's layer scope? — STOP and name the correct worker if not

**Workers check before writing (`## Preconditions`):**
- Does the target file/module NOT exist? (before `create-*` skills — avoid overwriting)
- For direct edits to existing artifacts: confirm the file exists before `Read` + `Edit`
- Are required dependencies available?

**Workers check before returning (`## Output`):**
- Does each created file exist on disk? (`Glob`)
- Does each file contain the expected primary class or function? (`Grep`)
- Only list paths that pass both checks

**Orchestrators check after each worker spawn:**
- Does the worker response contain an `## Output` section?
- Do all listed paths exist on disk?
- If either check fails: STOP — do not proceed to the next phase

When any check fails: return a clear, actionable message — never partially execute or silently continue.

**Agent Memory Governance:**

**What to remember:** Confirmed patterns, module-specific conventions not in reference docs, recurring mistakes, user-confirmed preferences.

**What NOT to remember:** Current task details, anything already in `CLAUDE.md` or `reference/`, unverified single-file observations, git history.

**Hygiene rules:** Keep `MEMORY.md` under 200 lines; use topic files for detailed notes; review and prune stale memories.

**Agent Naming Convention:**

| Type | Suffix | Example |
|---|---|---|
| Orchestrator | `-orchestrator` | `builder-feature-orchestrator.md`, `builder-groom-orchestrator.md` |
| Planner | `-planner` | `builder-feature-planner.md`, `builder-domain-planner.md` |
| Worker | `-worker` | `builder-feature-worker.md`, `detective-debug-worker.md` |

Format: `<persona>-<domain>-<role>.md`

Every agent that belongs to a persona must be prefixed with the persona name. This makes the persona assignment explicit from the filename alone and prevents collisions as the agent roster grows.

| Pattern | Example | When to use |
|---|---|---|
| `<persona>-<domain>-<role>` | `builder-feature-orchestrator`, `detective-debug-worker` | Agent inside a persona folder (`lib/core/agents/<persona>/`) |
| `<domain>-<role>` | `perf-worker`, `prompt-debug-worker` | Flat agent with no persona yet (`lib/core/agents/`) — prefix added when a persona is assigned |

> The filename now tells you the persona AND the agent type instantly — no need to open the file.

---

### 3. Skills = Hands (Thin Procedures)

Skills are focused, reusable workflow procedures. Each skill:

- Does one thing only
- References architecture docs — never embeds them
- Has no branching logic — agent decides which skill to call

**Skill size rule — contain no more than the type demands:**

| Type | Natural size | Reason |
|---|---|---|
| P — Procedure | Short — ~10–30 lines | Thin create-only procedure; logic belongs in the worker |
| W — Workflow | Scales with workflow complexity | Owns the full runtime — may do its own work or delegate to agents. Grows with the workflow it drives. |

There is no universal line limit. The constraint is not length — it is scope. A skill that grows because it is doing what a worker should do is wrong. A skill that grows because its type genuinely requires more steps is correct.

> Naming: `<layer>-<action>-<target>`. Platform-contract skills use `create-*` for new artifact creation only — there are no `update-*` skills. Skills are either **core-dependency** (same name on all platforms) or **platform-specific** (one platform only) — see [persona-builder.md](persona/builder.md).

**Workflow skill naming — persona prefix rule:**

Every Type W skill that is the entry point for a persona must be prefixed with the persona name: `<persona>-<action>`. This makes the relationship between skill and persona explicit at a glance and prevents naming collisions as the persona roster grows.

| Pattern | Example | When to use |
|---|---|---|
| `<persona>-<action>` | `builder-build-feature`, `detective-debug`, `auditor-arch-review` | Type W workflow skill that enters a persona workflow |
| `<persona>-<layer>-<action>-<target>` | `builder-domain-create-entity`, `builder-data-create-mapper` | Type P procedure skill called by a worker |

> Exception: standalone utility skills with no persona owner (e.g. `release`, `agentic-perf-review`) are named descriptively without a prefix until a persona is assigned.

**Preloading skills:**

Agents load their procedure skills at startup via the `skills` field — full skill content is injected at startup. This gives agents full procedural knowledge without embedding it in their body. Same procedures are reusable across multiple agents. One definition, updated once.

**Token budget guideline:**
- Preload skills the agent needs in >50% of its invocations
- Load on demand (via `Read`) skills needed rarely or only in edge cases
- Monitor total preloaded size — if it exceeds ~500 lines, split the agent or move low-frequency skills to on-demand

**Three consumer modes:**

Downstream projects interact with shared agents, skills, and reference docs in one of three modes:

| Mode | Applies to | Mechanism | When to use |
|---|---|---|---|
| **Use** | agents, skills, reference | Shared symlink → submodule file | Works as-is — standard workflow |
| **Extend** | agents only | Shared symlink + `agents.local/extensions/<name>.md` | Add behavior without losing submodule updates |
| **Override** | agents, skills, reference | Real file in `*.local/` | Fundamentally different behavior needed |

Extension files contain only the delta — not a full copy. Updates to the submodule are inherited automatically.

Reference docs are override-only (no extension mechanism) — they are structured with `## Section` headers and line counts that agents Grep by offset. Appending to a reference doc would corrupt those offsets and break the Grep contract.

**Local directories and their scope:**

| Directory | Override | Extend | Notes |
|---|---|---|---|
| `agents.local/` | ✓ | ✓ via `extensions/` | Workers check `extensions/<name>.md` at the end of their run |
| `skills.local/` | ✓ | — | Replace the whole skill dir |
| `reference.local/` | ✓ | — | Shadows platform/core reference docs; override-only by design |

> Skills have invocation types (A, T, U) — see [Taxonomy §Skills — By Invocation Type](#skills--by-invocation-type) for the full breakdown and decision rules.

---

### 4. Official Docs Compliance

Every design decision must comply with Claude Code's official documentation.

**Compliance checklist:**
- Skill directories follow `.claude/skills/<name>/SKILL.md` convention
- Agent files follow `.claude/agents/<name>.md` convention
- Frontmatter fields use only documented keys
- Memory scopes and permission modes use documented values

Confirmed undocumented field: `agents` — not in the official spec (verified against official docs 2026-05-09). Claude likely treats unknown frontmatter keys as hints. Use with awareness that it may change or be ignored in future versions. Runtime delegation always happens via the `Agent` tool — `agents:` is a static declaration for human and tooling readability, not a guaranteed runtime mechanism.

---

### 5. Convention Enforcement — Self-Auditing Architecture

The agentic system enforces its own conventions through automated review — the same principle applied recursively. Convention compliance tooling audits agent and skill files for structural violations before they reach downstream consumers.

> For the internal reviewer setup, checklist, and severity levels, see [submodule-repo-structure.md — Convention Compliance System](submodule-repo-structure.md#convention-compliance-system).

---

## Reference

**Three-tier structure:**

| Tier | Location | What goes here |
|---|---|---|
| 1 | `CLAUDE.md` | Universal rules applying to every task — naming, principles, build command. ~1 page max |
| 2 | Agent body | Decision logic for that agent only — what to do, when to do it |
| 3 | `.claude/reference/` | Shared deep reference — patterns, examples, conventions. Loaded on demand via Grep-first |

> Folder structure for reference docs: see [submodule-repo-structure.md](submodule-repo-structure.md).

**Reference vocabulary — Topic and Term:**

Reference docs are organized around two levels:

- **Topic** — the subject area a reference file covers. Platform-agnostic. A Topic is not engineering-specific: `domain.md` covers the domain topic for engineering; a future `components.md` would cover the design components topic; a `user-stories.md` would cover a requirements topic. One reference file per topic per platform.
- **Term** — the canonical name for one concept within a topic. Each `##` section heading is a Term. Terms are the agent's grep keys — one Term = one name = one `##` heading, everywhere across all platforms. If platform files use different headings for the same concept, the grep misses.

| Level | Example | Rule |
|---|---|---|
| Topic | `domain` | One reference file pair per topic per platform |
| Term | `UseCase` | Same `##` heading on every platform that implements it |
| Theory file | what a UseCase IS | `lib/core/reference/code-architecture/<topic>-theory.md` |
| Impl file | how to write a UseCase in Swift | `lib/platforms/<platform>/reference/code-architecture/<topic>-impl.md` |

Theory lives in `lib/core/` — single source of truth, platform-agnostic. Impl lives per platform. Both land at `.claude/reference/code-architecture/` downstream via symlinks. The theory file answers *what* and *why*; the impl file answers *how* in that language and syntax. A worker Greps the theory file to understand the contract, then Greps the impl file to write the correct code. One Grep each. Never the full file.

**Placement decision rule — reference vs agent body:**

| Put it in reference if… | Keep it in the agent body if… |
|---|---|
| It is a fact true regardless of who reads it | It is an instruction specific to this agent's workflow |
| It is an invariant, contract, or architectural principle | It is a decision: when to run, what to check, what to do on failure |
| Multiple agents need the same knowledge | Only this agent needs it |
| Removing it from the agent would lose shared truth | Removing it from the agent would lose execution behavior |

> One-line test: can you state it as a rule without saying "you"? If yes — reference. If it only makes sense addressed to the agent — agent body.

**Search Protocol (decision gate):**

Before any `Read` call, workers answer: "Do I need the full file, or just a specific symbol/section?"

| What you need | Tool |
|---|---|
| A specific class, function, or type | `Grep` for the name |
| A section of a reference doc | `Grep` for the section heading |
| The full file structure (style-matching a new file) | `Read` — justified |
| Whether a file exists | `Glob` |

Read a full file only when: (a) you need its complete structure to write a new matching file, or (b) Grep returned no results. Check `reference/index.md` first if uncertain which file covers a topic.

> Read:Grep ratio should stay below 3. A ratio above 6 is a P6 violation.

**Authoring rule — section line counts:**

Every `##` section heading in a reference doc must carry a line-count comment: `## Section Name <!-- N -->` where N is the number of lines from this heading to the line before the next `##` heading (or EOF for the last section). This is not cosmetic — agents extract N as the `limit` in `Read(file, offset=heading_line, limit=N)` to read exactly one section without loading the whole file. A missing or non-integer `<!-- N -->` forces a full-file Read.

```markdown
## DTOs <!-- 35 -->        ← correct: integer line count
## Mappers <!-- stub -->   ← wrong: agent cannot extract a limit
## Data Sources            ← wrong: no comment at all
```

`arch-check-conventions` enforces this — a missing integer is a Warning violation.

**Authoring rule — canonical Terms (ubiquitous language):**

Every `##` section heading in a cross-platform reference doc is a **Term** — the canonical name for one concept within a topic, and the exact grep key an agent searches for across all platforms. The heading must be identical across all platform files that cover the same concept.

This is *Ubiquitous Language* from Domain-Driven Design applied to agent tooling. One concept = one Term = one `##` heading, everywhere. No synonyms at the `##` level. Platform-specific terminology belongs in the body, not the heading.

```markdown
## Repository Interfaces <!-- 31 -->
In Swift, these are declared as protocols...   ← platform dialect lives here

## Repository Protocols <!-- 31 -->            ← wrong: breaks agent grep across platforms
```

| Contract | Axis | Rule |
|---|---|---|
| Vertical (line count) | Within one file | `## Section <!-- N -->` — agents extract N as read limit |
| Horizontal (canonical heading) | Across all platforms | Same `##` text for the same concept — agents grep once, find all platforms |

When adding a new section to a platform reference file, check whether the same concept exists in other platforms first. If it does, use that heading exactly. If it's net-new, choose a platform-agnostic term and apply it to all platforms that need it.

---

## Taxonomy

### Persona

A named group of related agents serving a coherent workflow.

Requirements:
- Lives in `lib/core/agents/<persona>/`
- Has at least one worker or orchestrator
- Agents within the group relate to and can depend on each other
- Requires a `.pkg` file for selective installation

Shared to all downstream projects via symlink. Current personas: `builder`, `detective`, `tracker`, `auditor`, `installer`.

> A persona is not just a folder. It represents a coherent workflow. Do not group unrelated agents into a persona subdirectory.

### Agents

#### By Role

| Role | Subordinates | Can write files? | Has `agents` field? | Has `skills` field? |
|---|---|---|---|---|
| Orchestrator | None — returns Decision blocks to the calling skill | Plan artifacts only (`plan.md`, `context.md`) in synthesize mode — never source files | No | No |
| Planner | None — spawned by the entry skill, reports findings back to skill | No writes — read-only tools only (`Glob`, `Grep`, `Read`) | No | No |
| Worker | Skills via `related_skills` | Yes — source files only | No | Yes — skills injected at startup |

**Orchestrator — brain-only decision maker:**

An orchestrator is a pure reasoning agent. It decides what to do and returns structured Decision blocks — it never spawns agents or writes source files directly.

- Accepts modes from the calling skill: `gather-intent`, `gather-intent-prefilled`, `process-findings`, `synthesize`, `execute-approved-plan`, `resume`
- Returns `Decision: spawn-planners` (which layers, why), `Decision: converged`, `Decision: spawn-worker`, or `Decision: blocked`
- In `synthesize` mode: writes `plan.md` and `context.md` to the runs directory — the only files an orchestrator may write
- The calling skill owns all agent spawning, the convergence loop, and user interaction

**Planner — layer explorer:**

A planner explores one CLEAN layer and returns structured findings. It is always read-only with respect to source code.

- Restricted to read-only tools (`Glob`, `Grep`, `Read`) — it physically cannot write files
- Scoped to its own layer's directories and artifact types
- Returns findings including `### Impact Recommendations` — which other layers are affected and why
- Spawned by the entry skill (not the orchestrator) based on the orchestrator's Decision block

Sub-planners are all leaf agents: they explore, report, and return. No further spawning.

> Orchestrators may spawn other orchestrators when the inner orchestrator represents a fully bounded sub-workflow. The outer orchestrator owns the top-level state file and final report.

#### By Scope

| Scope | Location | Ships downstream? |
|---|---|---|
| **Persona agent** | `lib/core/agents/<persona>/` | Yes — all platforms |
| **Platform agent** | `lib/platforms/<platform>/agents/` | Yes — matching platform only |
| **Project agent** | `.claude/agents.local/` | No — project-owned, not in this repo |

> Persona agents must be platform-agnostic — no platform paths, framework references, or language syntax in the body (Critical per P6).

### Skills

#### By Invocation Type

| Type | Config | Who triggers | Use for |
|---|---|---|---|
| **P — Procedure** | `user-invocable: false` | Worker (agent) only | Thin create-only procedures |
| **W — Workflow** | `user-invocable: true` | User only | User entry point — owns and runs the workflow. Simple workflows do their own work; complex ones delegate to agents. |

> For automated bash execution without model involvement, use hooks in `settings.json` — not a skill.

**Why no default skill type (invocable by both user and agent):** Every default skill's description loads into the main session context on every turn. Types P and W eliminate this overhead.

#### By Scope

| Scope | Location | Ships downstream? |
|---|---|---|
| **Toolkit skill** | `lib/core/skills/` | Yes — all platforms. Platform-agnostic, intended for use in downstream projects. |
| **Platform-contract skill** | `lib/platforms/<platform>/skills/contract/` | Yes — matching platform. Same name across all platforms; each implements for its syntax — called by persona workers. Lands flat in `.claude/skills/<name>/` downstream. |
| **Platform-only skill** | `lib/platforms/<platform>/skills/` (flat) | Yes — matching platform only. Called by platform agents. |
| **Project skill** | `.claude/skills.local/` | No — project-owned, not in this repo. |
| **Repo skill** | `.claude/skills/` | No — internal tooling only. Used by this repo's internal agents; never symlinked to downstream projects. |

> "Core-dependency skill" used in earlier sections of this doc refers to platform-contract skills — skills all platforms must implement under the same name (`builder-domain-create-entity`, `builder-data-create-mapper`, etc.).

#### Valid Type × Scope Combinations

Not all combinations are meaningful. Use this as the decision gate when adding a new skill:

| Scope | P — Procedure | W — Workflow |
|---|---|---|
| Toolkit | — | ✓ |
| Platform-contract | ✓ | — |
| Platform-only | ✓ | ✓ |
| Project | ✓ | ✓ |
| Repo | ✓ | ✓ |

> Toolkit skills are always user-facing (Type W) — agents don't call them, workers call platform-contract skills instead. Platform-contract skills are always Type P — they're called by workers programmatically, never by users directly.

### Reference Docs

#### By Scope

| Scope | Location | Ships downstream? |
|---|---|---|
| **Core reference** | `lib/core/reference/code-architecture/` | Yes — all platforms. Contains `<topic>-theory.md` (what/why, platform-agnostic, single source of truth). |
| **Platform reference** | `lib/platforms/<platform>/reference/code-architecture/` | Yes — matching platform. Contains `<topic>-impl.md` (how in that language). |
| **Project reference** | `.claude/reference.local/` | No — project-owned, not in this repo. Overrides platform docs for project-specific conventions. |

---

## Anatomy

### Anatomy of a Persona

A persona is composed of layered components that connect user intent to executed code. Each layer has a defined role, authority boundary, and handoff contract.

```
User
 │
 ▼
Workflow Skill (Type W)     — routes (resume vs new), pre-loads context, builds spawn prompt, owns convergence loop, spawns agents, approval
 │
 ▼  (gather-intent / decision round)
Orchestrator               — brain only; returns Decision blocks; never spawns agents or writes files
 │
 │  Decision: spawn-planners
 ▼
Trigger Skill              — spawns planners in parallel per round; accumulates findings
 │
 ▼  (sends findings back each round)
Orchestrator               — reads impact recommendations; decides: more rounds or converged?
 │
 │  Decision: converged → Trigger Skill synthesizes plan → user approval
 │  Decision: spawn-worker
 ▼
Trigger Skill              — spawns Worker with plan + context injected inline
 │
 ▼
Worker                     — reads plan, calls skills, writes source files, validates output
 │
 ▼
Skill(s)                   — concrete platform implementation (one per artifact type)
```

Not every persona uses all layers. A simple persona may have only a trigger skill + worker. A complex one adds an orchestrator, planners, and multiple workers. The anatomy is the same regardless of how many layers are present.

**Handoff contracts — what each layer passes to the next:**

| From → To | What is passed | What is never passed |
|---|---|---|
| Trigger Skill → Orchestrator | Intent / mode + accumulated findings (per round) | Raw file reads from the main session |
| Orchestrator → Trigger Skill | Structured Decision block (`spawn-planners`, `converged`, `spawn-worker`, `blocked`) | Agent spawns or file writes |
| Trigger Skill → Planner | Feature name, platform, module-path + mode instruction | Orchestrator's internal reasoning |
| Planner → Trigger Skill | Structured findings block including `### Impact Recommendations` | Source file paths or contents |
| Trigger Skill → Worker | `plan.md` + `context.md` injected inline | File paths only (contents always inlined) |
| Worker → Skill | Artifact name, target path, reference doc path | Cross-layer context |
| Worker → Trigger Skill | `## Output` section with Glob+Grep-verified paths | Partial or unverified paths |

**State files — written and read across the lifecycle:**

| File | Written by | Read by | Purpose |
|---|---|---|---|
| `state.json` | Orchestrator (after each phase) | Trigger skill (resume routing) | Phase completion + `next_phase` pointer |
| `plan.md` | Planner | Worker | Per-artifact execution instructions |
| `context.md` | Planner | Trigger skill (context relay) | Key symbols, conventions, existing artifacts |

> A persona without a trigger skill is incomplete. The trigger skill is the only supported entry path — it owns routing, context relay, and spawn prompt construction.

---

## Decision Rules

| Situation | Where it goes |
|---|---|
| New CLEAN-layer behaviour, same on all platforms | Core worker |
| New orchestration flow, same on all platforms | Core orchestrator |
| New code generation pattern for one platform | Platform-contract skill (same name, platform implements) → `lib/platforms/<platform>/skills/contract/` |
| Workflow too platform-specific for any core agent | Platform agent + platform skill → `lib/platforms/<platform>/skills/` (flat) |
| Architecture reference knowledge (any topic) | `lib/core/reference/code-architecture/<topic>-theory.md` (what/why) + `lib/platforms/<platform>/reference/code-architecture/<topic>-impl.md` (how) — both land at `.claude/reference/code-architecture/` downstream |
| Architecture reference knowledge (platform-specific, no theory counterpart) | `lib/platforms/<platform>/reference/` (flat) |

**Planner vs Worker — when to use which:**

| Work profile | Recommended path |
|---|---|
| Contained, well-understood (1–3 artifacts, clear scope, single layer) | Worker directly — overhead of planning exceeds the benefit |
| Cross-layer feature build, multiple artifact types, or uncertain existing state | Planner first → worker — exploration cost is front-loaded, execution is zero-rework |
| Modification to an existing artifact (targeted edit) | Worker directly with context.md Key Symbols if available |
| Large-scale change across many modules or unknown conventions | Planner first — sub-planners explore in parallel, findings aggregated before a single line is written |

> The rule of thumb: if a worker would spend significant time exploring before it can execute, a planner is the better investment. If the scope is clear and bounded, skip the planner and go straight to the worker.

> **Build-directly is a deliberate opt-out, not a default.** It skips all layer isolation guarantees — `feature-worker` makes layer assignment decisions inline with no plan, no human gate, and no tool restriction. The resume routing gate limits the risk: build-directly is only reachable for brand-new features with no prior run. Any feature that was previously planned always resumes against its existing `plan.md` — the worker never re-makes layer decisions that were already validated.

> For execution examples and the current agent roster, see [persona-builder.md](persona/builder.md).

---

## Why This Architecture

| Goal | How it's achieved |
|---|---|
| Token efficiency | Isolated context; Search Protocol decision gate; Haiku for mechanical workers; file paths only between phases; orchestrator state files prevent mid-run re-reads; context relay — skill reads runs context from disk and inlines into spawn prompt, spawned agent pays zero pre-flight read cost |
| Modular knowledge | Skills preloaded, not embedded |
| Single source of truth | `reference/` Grep-accessed, never duplicated |
| Safe destructive operations | Use hooks in `settings.json` for automated bash execution without model involvement |
| Reusability | Same skill preloaded into multiple workers |
| Maintainability | Update one skill → all workers get the update |
| Multi-platform scalability | Add `lib/platforms/<platform>/skills/` — no agent changes |
| Selective installation | Persona `.pkg` files |
| Self-enforcing conventions | Internal arch-reviewer catches violations before downstream consumers |
| Clear distributable boundary | `lib/` = ships downstream; everything outside = internal tooling |
| Agent prompt quality | `prompt-debug-worker` surfaces ambiguous instructions when perf scores flag low D1–D7 |

---

## Official Documentation

| Topic | URL |
|---|---|
| Subagents | https://code.claude.com/docs/en/sub-agents |
| Skills | https://code.claude.com/docs/en/skills |
| Context window | https://code.claude.com/docs/en/context-window |
| Agent Teams | https://code.claude.com/docs/en/agent-teams |
| Hooks | https://code.claude.com/docs/en/hooks |
| MCP | https://code.claude.com/docs/en/mcp |
| Memory & CLAUDE.md | https://code.claude.com/docs/en/memory |
| Settings | https://code.claude.com/docs/en/settings |
| Permissions | https://code.claude.com/docs/en/permissions |

---

## Changelog

See git history for this file.
