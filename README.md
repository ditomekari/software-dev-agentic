# software-dev-agentic

> Claude Code toolkit for Clean Architecture projects — v5.2.0

A git submodule that wires AI agents, skills, hooks, and architecture reference docs into your project's `.claude/` directory. Version-controlled in one place, shared across all platforms and projects.

**Platforms:** Web (Next.js 15) · iOS (Swift/UIKit) · Flutter · Android

---

## How it works

Add this repo as a submodule at the project root under `software-dev-agentic/`. The setup script symlinks agents and skills into `.claude/agents/` and `.claude/skills/` — Claude Code, Gemini CLI, and GitHub Copilot all pick them up from there. Your project code stays untouched.

```
your-project/
  software-dev-agentic/    ← this repo (submodule, at project root)
  .claude/
    agents/                → symlinks into submodule
    skills/                → symlinks into submodule
    agents.local/          ← your project-specific overrides (never touched by sync)
```

Agents are organized into **personas** — coherent workflow groups. All personas are installed by default.

---

## Setup

### Starting a new project

```bash
# 1. Create your project (example: Next.js)
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir
cd my-app

# 2. Add the submodule
git submodule add https://github.com/mekaripaper/software-dev-agentic software-dev-agentic

# 3. Wire everything — symlinks all agents, skills, hooks, and reference for the platform
software-dev-agentic/scripts/setup-symlinks.sh --platform=web
# or
software-dev-agentic/scripts/setup-symlinks.sh --platform=ios
```

Open Claude Code and use trigger skills (`/builder-build-feature`, `/detective-debug`, etc.) as the entry point.

---

### Adding to an existing project

```bash
git submodule add https://github.com/mekaripaper/software-dev-agentic software-dev-agentic

software-dev-agentic/scripts/setup-symlinks.sh --platform=web
# or
software-dev-agentic/scripts/setup-symlinks.sh --platform=ios
```

The script wires symlinks, copies `CLAUDE.md`, and sets up `settings.local.json`. Re-running is safe — existing files and local overrides are never overwritten.

---

## Keeping up to date

```bash
software-dev-agentic/scripts/sync.sh --platform=<platform>
```

Pulls the latest, re-runs symlink setup (idempotent), and reminds you to commit the updated submodule pointer. Local overrides in `agents.local/` and `skills.local/` are never touched.

---

## What's included

### Agents — by persona

**builder** — feature construction across CLEAN layers

| Agent | Purpose |
|---|---|
| `builder-feature-orchestrator` | Brain of the builder persona — decides which planners to spawn each round, synthesizes plan.md + context.md, instructs entry skill to spawn worker. Never spawns agents or writes source files directly. |
| `builder-feature-worker` | Execute an approved feature plan layer by layer |
| `builder-backend-orchestrator` | Build domain + data layers when presentation exists or will be built separately |
| `builder-groom-orchestrator` | Groom a Jira ticket against the codebase — detects scope from AC, returns which planners to run, synthesizes grooming summary |
| `builder-domain-planner` | Discover Domain layer — entities, use cases, repository interfaces. Returns findings + impact recommendations. Read-only. |
| `builder-data-planner` | Discover Data layer — DTOs, mappers, datasources, repository impls. Returns findings + impact recommendations. Read-only. |
| `builder-pres-planner` | Discover Presentation layer — StateHolders, screens, components. Returns findings + impact recommendations. Read-only. |
| `builder-app-planner` | Discover App layer — DI, routing, module, analytics, feature flags. Returns findings + impact recommendations. Read-only. |
| `builder-ui-worker` | Create or update screens and components bound to an existing StateHolder |
| `builder-test-worker` | Generate tests for any CLEAN layer |

**detective** — debugging and performance analysis

| Agent | Purpose |
|---|---|
| `detective-debug-orchestrator` | Investigate a bug through static analysis, form hypotheses, instrument code |
| `detective-debug-worker` | Trace a runtime error or unexpected behavior to its root cause |
| `detective-debug-log-worker` | Add or remove debug log statements for a specific investigation |
| `perf-worker` | Score agentic session performance across D1–D7 dimensions, write report |

**tracker** — issue and ticket lifecycle

| Agent | Purpose |
|---|---|
| `tracker-issue-worker` | Create or pick up a GitHub issue, open the feature branch, update backlog |
| `tracker-jira-ticket-worker` | Create Jira tickets under an epic from a platform breakdown list — fetches PRD and optional Figma context, generates requirement-focused descriptions |

**auditor** — architecture compliance

| Agent | Purpose |
|---|---|
| `auditor-arch-review-worker` | Audit code for CLEAN Architecture violations — layer boundaries, entity purity, DI |

**installer** — project setup

| Agent | Purpose |
|---|---|
| `installer-setup-worker` | Detect platform, scaffold the project, guide initial onboarding |

---

### Skills — by persona

**builder**

| Skill | Purpose |
|---|---|
| `/builder-build-feature` | Build or update a feature — resumes an existing run or starts a new one (plan-first or build-directly) |
| `/builder-plan-feature` | Plan then build — runs convergence planning loop (spawning only needed layer planners per round), shows approval prompt, then executes |
| `/builder-build-from-ticket` | One-shot build from a Jira ticket key or URL — non-interactive, convergence loop runs automatically, designed for CI |
| `/builder-backend` | Build Domain + Data layers only |
| `/builder-groom-ticket` | Groom a locally fetched Jira ticket against the codebase |
| `/builder-clear-runs` | Remove stale orchestrator run state from `.claude/agentic-state/runs/` |

**tracker**

| Skill | Purpose |
|---|---|
| `/tracker-jira-ticket` | Create Jira tickets under an epic from a platform breakdown list |
| `/tracker-issue` | Create or pick up a GitHub issue, create branch, update backlog |
| `/tracker-adjust-ticket` | Update the Session Adjustment section of a locally fetched ticket |

**detective**

| Skill | Purpose |
|---|---|
| `/detective-debug` | Trigger the debug orchestrator — collects bug intake then investigates |

**auditor**

| Skill | Purpose |
|---|---|
| `/auditor-arch-review` | Audit code for CLEAN Architecture violations |

**installer**

| Skill | Purpose |
|---|---|
| `/installer-setup` | Set up or reconfigure a project to use this toolkit |
| `/installer-doctor` | Audit the toolkit setup — submodule, symlinks, CLAUDE.md, settings, gh auth |
| `/installer-sync` | Pull the latest updates and re-link agents, skills, hooks, and reference docs |
| `/installer-update` | Sync to latest then verify the full installation end-to-end |

**utility**

| Skill | Purpose |
|---|---|
| `/agentic-perf-review` | Score a Claude session on D1–D7 dimensions, write a report |
| `/release` | Cut a new release — bumps VERSION, prepends CHANGELOG, commits, tags |

---

## Recommended Workflows

These are the recommended flows to try first. They cover the two most common day-to-day scenarios and give you a clear picture of how the personas work together. Start here before exploring individual agents or skills in depth.

---

### Workflow 1 — Tracker Persona

---

#### 1a — Create Jira Tickets from PRD or Confluence Doc

**When to use:** You have a PRD and a per-platform task breakdown and need to turn them into properly described Jira tickets.

**What you need before starting:**
- Atlassian MCP installed and authenticated
- Figma MCP (optional — for UI tickets with design specs)
- A Jira epic key to put the tickets under
- A breakdown list in this format:
  ```
  - [ADR] [UI+API] Show location marker on map: 2 days
  - [iOS] [UI+API] Show location marker on map: 2 days
  - [ADR] [UI] Show location accuracy perimeter: 1 day
  - [iOS] [UI] Show location accuracy perimeter: 1 day
  ```

Paste everything inline — the worker reads it all from your message:

```
/tracker-jira-ticket

epic_key: PROJ-1234
cloud_id: yourcompany.atlassian.net
project_key: PROJ
prd_source: https://yourcompany.atlassian.net/wiki/spaces/ENG/pages/123456789/Feature+PRD

breakdown:
- [ADR] [UI+API] Show location marker on map: 2 days
- [iOS] [UI+API] Show location marker on map: 2 days
- [ADR] [UI] Show location accuracy perimeter: 1 day
- [iOS] [UI] Show location accuracy perimeter: 1 day
```

If the PRD already links to Figma designs, you don't need to add `figma_links` — the worker will use what's in the PRD. Only add `figma_links` explicitly when the designs live in a separate Figma file not referenced in the PRD:

```
figma_links: https://figma.com/design/abc123/Feature-Screens?node-id=1-2
```

If any required input is missing, the worker will ask before proceeding.

The worker walks through the full flow automatically:

1. Parses the breakdown into tickets with story points
2. Fetches the PRD from Confluence (or uses your pasted text)
3. Fetches Figma design specs for `[UI]` and `[UI+API]` tickets
4. Generates a structured description per ticket: **Context** · **Scope of Work** · **Design** · **Acceptance Criteria**
5. Shows a preview table — you confirm before anything is created
6. Creates all tickets under the epic via Atlassian MCP

After tickets are created, fetch them as local `.md` files using any MCP tool (e.g. Atlassian MCP). This gives Claude a local copy to read and update — the original Jira ticket is never modified directly.

---

#### 1b — Update Ticket Progress

**When to use:** After any work or discussion session — you don't need to have implemented anything. A design discussion, an architectural decision, or a set of resolved open questions is enough reason to run this. Record what was completed, decided, or clarified. Run this as often as needed; it never touches the original ticket description.

> **Note:** The ticket must be fetched locally first (see 1a). `/tracker-adjust-ticket` reads and updates the local `.md` file — it does not pull from Jira directly.

Paste your session notes inline and end with `/tracker-adjust-ticket`. Example:

```
Session update:

Work items completed:
- Verified old cache mechanism in Connection.swift is no longer used — safe to remove
- Migrated GetLocationListUseCase to new datasource pattern
- Added force: Bool parameter to UseCaseType — all use cases updated

Decisions:
- Replaced old caching layer entirely — it was unused and conflicting with OkHttp cache
- Chose to add force param to UseCaseType protocol rather than a separate ForceCallUseCase wrapper

Open questions resolved:
- Confirmed with backend: /location/list endpoint supports cache-control headers, no extra param needed

Still open:
- Need to verify force call behavior on poor network — test on device before closing

/tracker-adjust-ticket path/to/TICKET-123.md
```

Claude writes a `## Session Adjustment` section into the local ticket file with work items, decisions, and open questions — nothing else in the file is touched.

When you're ready to start building, move to **Workflow 2**.

---

### Workflow 2 — Builder Persona: Groom then build from a local ticket

**When to use:** You have a Jira ticket and want Claude to understand the codebase context, plan the implementation, and execute it layer by layer.

This is the most common day-to-day flow. Follow the steps in order — each one sets up the next.

---

**Step 1 — Fetch the ticket locally**

Use any MCP tool (e.g. Atlassian MCP) to fetch the Jira ticket and save it as a local `.md` file. This is the single source of truth Claude reads throughout the workflow.

---

**Step 2 — Groom the ticket against the codebase**

This is where you give Claude the context that isn't in the ticket. Open a new session, paste your notes — open questions, relevant files, constraints, things to investigate — then end the message with `/builder-groom-ticket`. You don't need a separate prompt; everything goes in one message.

Example:

```
We have some things to address:

1. Cache mechanism
   - In @Talenta/Utils/Connection.swift and @Talenta/Middleware/Network/Connector.swift
     there's an old caching layer that hasn't been maintained.
   - We need to decide: keep it, improve it, or replace it.

2. Affected APIs — migration needed
   - Some still use the old @Talenta/Middleware/Network/Interface/ pattern
   - Target pattern: @Talenta/Module/TalentaDashboard/Data/DataSource/DashboardRemoteDataSource.swift

3. Force call bypassing TTL
   - Need to pass force: Bool from presentation down to the data layer
   - Considering adding it to UseCaseType — but that means refactoring all use cases

/builder-groom-ticket path/to/TICKET-123.md
```

**Output:** the ticket file gets a `## Session Adjustment` section added — layer mapping, concrete work items, decisions, and open questions. This becomes the input for the next step.

---

**Step 3 — Start a fresh session**

Run `/clear` or open a new Claude Code session. Grooming can consume significant context — starting fresh keeps the build session focused and token-efficient.

---

**Step 4 — Plan and build**

You can be as brief or specific as you like. A minimal prompt:

```
Let's work on the work items in this ticket.

/builder-plan-feature path/to/TICKET-123.md
```

Or be more directive if you want to focus on specific items:

```
Let's work on the work items in this ticket. Focus on the API migration items first, skip the force call refactor for now.

/builder-plan-feature path/to/TICKET-123.md
```

Claude reads the groomed ticket (including the Session Adjustment), runs the convergence planning loop — spawning only the layer planners relevant to the work items, expanding scope if planners detect cross-layer impact — and presents a plan for your approval. Once you approve, `builder-feature-worker` executes the implementation layer by layer — Domain → Data → Presentation → UI.

---

**Step 5 — Update ticket progress**

```
/tracker-adjust-ticket path/to/TICKET-123.md
```

After the build, update the ticket with what was completed this session: which work items are done, decisions made, and any remaining open questions. Keeps the ticket as the living record of the feature.

---

**Step 6 — Verify and iterate**

Run the app, review the output, and ask Claude to adjust anything. If work items remain from the Session Adjustment, loop back to Step 4 for the next session.

---

## Architecture

All agents enforce a three-layer Clean Architecture:

```
Presentation  →  Domain  ←  Data
```

- **Domain** — pure business logic, zero framework imports. Entities, use cases, repository interfaces.
- **Data** — implements domain interfaces. Remote/DB data sources, mappers, repository implementations.
- **Presentation** — StateHolder (ViewModel / BLoC / Presenter), UI screens, navigation. Depends only on domain.

Platform skill implementations handle the language and framework specifics:

| Platform | Language | UI framework | State management |
|---|---|---|---|
| Web | TypeScript | Next.js 15 / React | Custom hooks |
| iOS | Swift | UIKit | ViewModel + Coordinator |
| Flutter | Dart | Flutter | BLoC |
| Android | Kotlin | — | Presenter |

Architecture reference docs live in `lib/core/reference/code-architecture/` (universal) and `lib/platforms/<platform>/reference/` (platform-specific).

---

## Design docs

Local source of truth (this repo):
- [`docs/principles/core-design-principles.md`](docs/principles/core-design-principles.md) — all 15 principles, full taxonomy, decision rules
- [`docs/principles/submodule-repo-structure.md`](docs/principles/submodule-repo-structure.md) — cross-platform submodule architecture

Published view (Confluence):
- [Agentic Coding Assistant — Core Design Principles](https://jurnal.atlassian.net/wiki/spaces/~611df3da650a26006e44928d/pages/51126370416)
- [Shared Agentic Submodule Architecture — Cross-Platform Scaling](https://jurnal.atlassian.net/wiki/spaces/~611df3da650a26006e44928d/pages/51129909710)

---

## .gitignore recommendations

Add to your downstream project's `.gitignore`:

```gitignore
# Claude Code — agentic state (delegation flags, session state, run artifacts)
.claude/agentic-state/
```

This directory holds delegation flags, session tracking, and per-feature orchestrator run state. It is local state and should not be committed.
