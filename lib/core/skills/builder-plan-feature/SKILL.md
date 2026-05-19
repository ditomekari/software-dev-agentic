---
name: builder-plan-feature
description: Plan then build a feature — optionally resolves external inputs (Jira, PRD, Figma, local .md), gathers intent via builder-feature-orchestrator, runs the convergence planning loop (spawning only the needed layer planners per round), shows an interactive approval prompt, then executes with builder-feature-worker on approval.
user-invocable: true
allowed-tools: Agent, AskUserQuestion, Bash, Read, WebFetch
---

## Step 0 — Resolve Inputs

Parse all arguments passed to this skill. Classify each by pattern:

| Pattern | Type | Fetch via |
|---|---|---|
| URL containing `jira` or `atlassian`, or bare ticket ID (e.g. `PROJ-123`) | Jira ticket | Atlassian MCP tool (attempt; failure = not configured) |
| URL containing `figma.com` | Figma design | Figma MCP tool (attempt; failure = not configured) |
| Any other URL | PRD / doc | `WebFetch` |
| Path ending in `.md` | Local file | `Read` |

If no arguments are provided, skip this step — proceed to Step 1 with `resolved_inputs = []`.

Attempt all fetches in parallel. Collect:
- `resolved_inputs` — successfully fetched items, each as `{ type, source, content }`
- `failed_inputs` — items that could not be fetched, each as `{ type, source, reason }`

If `failed_inputs` is non-empty, call `AskUserQuestion`:

```
question    : "Some inputs couldn't be fetched: <list each with reason>. What would you like to do?"
header      : "Input Fetch"
multiSelect : false
options     :
  - label: "Continue",         description: "Proceed with the inputs that were successfully resolved"
  - label: "Provide manually", description: "Paste or describe the missing content before continuing"
  - label: "Cancel",           description: "Stop and retry after fixing the inputs"
```

**Continue** → proceed with `resolved_inputs` as-is.

**Provide manually** → for each item in `failed_inputs`, ask the user to paste or describe the content. Append each to `resolved_inputs`. Then proceed.

**Cancel** → stop.

## Step 1 — Gather Intent

Spawn `builder-feature-orchestrator` with mode `gather-intent`:

> **Mode: gather-intent**
>
> <if resolved_inputs is non-empty, include the following block — otherwise omit>
> **Resolved Inputs:**
> <for each item in resolved_inputs: "### <type> — <source>\n<content>">
>
> Ask the user for feature intent. Return a `Decision: spawn-planners` block when done.

Wait for the orchestrator to return. Extract the `Decision: spawn-planners` block.

Initialize:
- `visited` = [] (empty set of explored layers)
- `all_findings` = [] (accumulated planner findings across all rounds)
- `round` = 1

## Step 2 — Planning Convergence Loop

Repeat until the orchestrator returns `Decision: converged` or `Decision: blocked`.

### 2a — Spawn planners for this round

From the current `Decision: spawn-planners` block, read the `spawn:` list. Spawn each listed planner **in parallel** (single Agent tool call with all planners in that round):

- `builder-domain-planner` — if `domain` is in the spawn list
- `builder-data-planner` — if `data` is in the spawn list
- `builder-pres-planner` — if `pres` is in the spawn list
- `builder-app-planner` — if `app` is in the spawn list

Pass to each planner: feature name, platform, module-path (from orchestrator's gather-intent output).

Wait for all planners in this round to complete.

Add each spawned layer to `visited`. Append each planner's full findings block to `all_findings`.

### 2b — Send findings to orchestrator

Spawn `builder-feature-orchestrator` with mode `process-findings`:

> **Mode: process-findings**
>
> Round: <N>
> Visited layers: <comma-separated list from visited set>
>
> **Accumulated Findings:**
> <paste full all_findings content>

Wait for the orchestrator's decision block.

- **`Decision: spawn-planners`** → increment `round`, go back to 2a
- **`Decision: converged`** → proceed to Step 3
- **`Decision: blocked`** → present the orchestrator's question to the user via `AskUserQuestion`, send the answer back to orchestrator as a follow-up `process-findings` call, then re-evaluate

**Max rounds guard:** If `round` reaches 4 without convergence, stop the loop and surface to the user:
> "Planning could not converge after 3 rounds. Open questions: <list from last blocked decision>. Please clarify before retrying."

## Step 3 — Synthesize Plan

Spawn `builder-feature-orchestrator` with mode `synthesize`:

> **Mode: synthesize**
>
> **All Accumulated Findings:**
> <paste full all_findings content>

Wait for the orchestrator to return the plan summary and write plan.md + context.md.

## Step 4 — Approve

Call `AskUserQuestion` immediately after synthesis — do NOT describe choices in prose:

```
question    : "What would you like to do with this plan?"
header      : "Plan"
multiSelect : false
options     :
  - label: "Approve",      description: "Execute this plan with builder-feature-worker"
  - label: "Discuss more", description: "I have questions or changes before this plan is finalized"
  - label: "Discard",      description: "Cancel and delete this plan"
```

**Approve** → proceed to Step 5.

**Discuss more** → address the engineer's questions inline. If the plan itself needs revision, re-run Step 3 (re-synthesize) with the updated requirements added to the findings context. Then call `AskUserQuestion` again with the same three options.

**Discard** → delete the most recent run directory:

```bash
rm -rf "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs/<feature>"
```

Stop.

## Step 5 — Execute

Update `status` in `plan.md` frontmatter from `pending` to `approved`.

Read `plan.md` and `context.md` from the run directory written in Step 3. Then spawn `builder-feature-worker`:

> Approved plan ready. Pre-loaded context below — do not re-read plan.md, context.md, or state.json.
>
> **plan.md**
> <content>
>
> **context.md**
> <content>
>
> Proceed directly to the first pending artifact.

## Step 6 — Unit Tests

Read `state.json` from the run directory. Extract all paths under `domain`, `data`, and `presentation` keys — these are the unit-testable artifacts. Skip `ui` and `app`.

Call `AskUserQuestion` immediately — do NOT describe choices in prose:

```
question    : "Run unit tests for created artifacts?"
header      : "Unit Tests"
multiSelect : false
options     :
  - label: "Yes",  description: "Generate unit tests for all created artifacts via builder-test-worker"
  - label: "Skip", description: "I'll run tests manually later"
```

**Yes** → spawn `builder-test-worker`:

> target: <comma-separated artifact paths from state.json>
> platform: <platform from plan.md frontmatter>

**Skip** → surface the paths as a reminder:

> Tests not generated. Run when ready:
> `/builder-test-worker` — targets: <paths>
