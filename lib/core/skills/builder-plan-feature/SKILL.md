---
name: builder-plan-feature
description: Plan then build a feature — optionally resolves external inputs (Jira, PRD, Figma, local .md), gathers intent via builder-feature-orchestrator, runs the convergence planning loop (spawning only the needed layer planners per round), shows an interactive approval prompt, then executes with builder-feature-worker (Domain/Data/Pres/App) followed by builder-ui-worker (UI layer) on approval.
user-invocable: true
allowed-tools: Agent, AskUserQuestion, Bash, Read, WebFetch
---

## Routing Contract

This skill is a pure router. Its only permitted direct operations:
- `Bash` — preflight existence checks and run-dir persistence writes only
- `Read` — only for explicit `.md` input files passed as arguments
- `WebFetch` — only for non-Figma URLs passed as arguments
- `AskUserQuestion` — approval prompts defined in each step

Never read source files, search the codebase, or write code. All exploration, planning, and implementation is exclusively delegated to orchestrator / planner / worker agents.

## Preflight — Detect Existing Runs

```bash
find "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs" -maxdepth 2 -name "plan.md" 2>/dev/null
find "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs" -maxdepth 2 -name "figma-groups.json" 2>/dev/null
```

Collect results as `found_plans` and `found_figma`. **Do not route yet.** Pass them to Step 1 so the orchestrator sees the user's intent alongside any existing runs before making a routing decision.

## Step 0 — Classify Inputs

Parse all arguments passed to this skill. Classify each by pattern:

| Pattern | Type | Action |
|---|---|---|
| URL containing `jira` or `atlassian`, or bare ticket ID (e.g. `PROJ-123`) | Jira ticket | Fetch inline via Atlassian MCP |
| URL containing `figma.com` | Figma design | Store in `pending_figma_urls` — fetch in Step 1.5 |
| Any other URL | PRD / doc | Fetch inline via `WebFetch` |
| Path ending in `.md` | Local file | Read inline via `Read` |

If no arguments are provided, skip this step — proceed to Step 1 with `resolved_inputs = []` and `pending_figma_urls = []`.

Fetch all non-Figma inputs inline now. Collect:
- `resolved_inputs` — successfully fetched non-Figma items: `{ type, source, content }`
- `pending_figma_urls` — Figma URLs deferred until feature name is known after Step 1
- `failed_inputs` — non-Figma items that could not be fetched: `{ type, source, reason }`

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
> <if found_plans or found_figma is non-empty, include:>
> **Existing runs:**
> \<found_plans list, or "(none)"\>
> **Existing figma groups:**
> \<found_figma list, or "(none)"\>
>
> <if resolved_inputs or pending_figma_urls is non-empty, include the following block — otherwise omit>
> **Resolved Inputs:**
> <for each non-Figma item: "### <type> — <source>\n<content>">
> <if pending_figma_urls is non-empty: "### Figma designs (pending fetch)\n<list each URL — will be fetched after feature name is confirmed>">
>
> Ask the user for feature intent. Surface any existing runs and let the user choose to continue or start fresh. Return a Decision block when done.

Wait for the orchestrator to return. Route based on the Decision block:

- **`Decision: discard-partial`** → `rm -rf "<run_dir from decision>"`. Re-spawn orchestrator in `gather-intent` mode (same inputs, minus the discarded path from `found_plans`/`found_figma`).
- **`Decision: resume-as-is`** → extract `run_dir`. Proceed directly to Step 5 (Execute).
- **`Decision: spawn-planners`** → extract `feature`, `platform`, `module_path`, `run_dir`. If `update_mode: true` also extract `completed_artifacts`, `open_questions`, `figma_groups`. Initialize `visited = []`, `all_findings = []`, `round = 1`. Proceed to Step 1.5 (if `pending_figma_urls` non-empty) or Step 2.

## Step 1.5 — Fetch Figma Inputs (skip if `pending_figma_urls` is empty)

`run_dir` is already known from the `Decision: spawn-planners` block — use it directly.

Spawn one `builder-figma-worker` per URL in `pending_figma_urls` — pass `figma_url`, `feature`, and `run_dir`. **Spawn all workers in parallel** (single Agent tool call).

Collect results from all workers:
- `figma_resolved` — workers that returned `## Figma Worker Output` blocks
- `figma_sections` — workers that returned `## Figma Section Detected` blocks
- `figma_failed` — failed fetches: `{ source, reason }`

**If `figma_sections` is non-empty** — expand each section into individual frame workers. For each section, spawn one `builder-figma-worker` per child frame **in parallel** (single Agent call across all children of all sections) — pass `figma_url` constructed as `https://www.figma.com/design/<fileKey>?node-id=<child_id>`, same `feature` and `run_dir`. Collect results and merge into `figma_resolved` and `figma_failed`.

If `figma_failed` is non-empty, call `AskUserQuestion`:

```
question    : "Some Figma frames couldn't be fetched: <list each with reason>. What would you like to do?"
header      : "Figma Fetch"
multiSelect : false
options     :
  - label: "Continue",  description: "Proceed with the frames that were successfully fetched"
  - label: "Cancel",    description: "Stop and retry after fixing the Figma inputs"
```

### Step 1.5b — Verify Figma Grouping (skip if `figma_resolved` is empty)

Spawn `builder-figma-worker` with mode `group-frames`:

> mode: group-frames
> run_dir: \<run_dir\>

Wait for the `## Figma Groups` output block. Extract `groups` as `figma_groups` and `review` (may be absent).

Build the grouping summary:
```
<for each group:>
• <screen> — states: <comma-separated state names>
<if review present:>

Needs your eye:
<for each review entry:>
• <frame>: <reason>
```

Call `AskUserQuestion`:

```
question    : "Figma frames grouped into screens. Does this look correct?

               <grouping summary>"
header      : "Figma Screens"
multiSelect : false
options     :
  - label: "Correct",  description: "Grouping looks right — proceed to planning"
  - label: "Adjust",   description: "The grouping needs changes before we continue"
```

**Correct** → store `figma_groups` and proceed.

**Adjust** → ask the user to describe corrections (which frames belong to which screen, any renames). Apply to `figma_groups`. Then proceed.

`figma_groups` structure carried forward:
```
[
  {
    screen: "<parent_frame>",
    states: [
      { state: "<state>", file: "<abs-path-to-.md>", layout_file: "<abs-path-to--layout.jsx>", screenshot: "<url>" },
      ...
    ]
  },
  ...
]
```

**Persist figma_groups to disk** — write immediately after grouping is confirmed:

```bash
cat > "<run_dir>/figma-groups.json" << 'EOF'
<figma_groups as JSON>
EOF
```

Initialize:
- `visited` = [] (empty set of explored layers)
- `all_findings` = [] (accumulated planner findings across all rounds)
- `round` = 1

Proceed to Step 2. Do not read widget files, grep the codebase, or write any code — all exploration, planning, and implementation is done by planners and workers.

## Step 2 — Planning Convergence Loop

Repeat until the orchestrator returns `Decision: converged` or `Decision: blocked`.

### 2a — Spawn planners for this round

From the current `Decision: spawn-planners` block, read the `spawn:` list. Spawn each listed planner **in parallel** (single Agent tool call with all planners in that round):

- `builder-domain-planner` — if `domain` is in the spawn list
- `builder-data-planner` — if `data` is in the spawn list
- `builder-pres-planner` — if `pres` is in the spawn list
- `builder-app-planner` — if `app` is in the spawn list

Pass to each planner: feature name, platform, module-path (from orchestrator's gather-intent or review-resume output).

**If `update_mode` is true** (resume path with new intent), also pass:
- `open_questions` — the user's stated issues from the Decision block, verbatim. Planners use these to focus on what needs fixing rather than doing a full greenfield sweep.
- `completed_artifacts` — list of already-built artifact names. Planners treat these as locked: report `exists` status, do not propose recreating them.

For `builder-pres-planner` specifically — if `figma_groups` was established in Step 1.5b or Step R0, also pass:
- The full `figma_groups` structure (screen → states + file paths) — do NOT inline file contents

Wait for all planners in this round to complete.

Add each spawned layer to `visited`. Append each planner's full findings block to `all_findings`.

**Persist findings to disk** — write after every round completes:

```bash
cat > "<run_dir>/findings-round-<N>.json" << 'EOF'
{
  "round": <N>,
  "visited": [<visited list>],
  "findings": "<all_findings for this round, escaped>"
}
EOF
```

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

**If `update_mode` is true** — archive the current plan before synthesizing:

```bash
N=$(ls "<run_dir>/plan-v"*.md 2>/dev/null | wc -l | tr -d ' ')
N=$((N + 1))
mv "<run_dir>/plan.md"    "<run_dir>/plan-v${N}.md"
mv "<run_dir>/context.md" "<run_dir>/context-v${N}.md"
```

Spawn `builder-feature-orchestrator` with mode `synthesize`:

> **Mode: synthesize**
>
> \<if update_mode is true:\>
> **update: true**
>
> **existing_plan:**
> \<content of archived plan-vN.md\>
>
> **existing_context:**
> \<content of archived context-vN.md\>
>
> **completed_artifacts:** \<comma-separated list\>
> \<end if\>
>
> **All Accumulated Findings:**
> \<paste full all_findings content\>

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

### Phase 1 — Domain / Data / Presentation / App

Read `plan.md` and `context.md` from the run directory. Spawn `builder-feature-worker`:

> Approved plan ready. Pre-loaded context below — do not re-read plan.md, context.md, or state.json.
>
> **plan.md**
> \<content\>
>
> **context.md**
> \<content\>
>
> Proceed directly to the first pending artifact.

**Checkpoint loop:** if the worker returns `## Context Checkpoint` instead of `## Layers Complete`, immediately re-spawn a fresh `builder-feature-worker` without user interaction:

> Resuming from context checkpoint. Pre-loaded context below — do not re-read plan.md, context.md, or state.json.
>
> **plan.md**
> \<content — re-read from disk\>
>
> **context.md**
> \<content — re-read from disk\>
>
> **Resume from:** \<next_artifact from checkpoint block\>
> **State file:** \<state_file from checkpoint block\>
>
> Read state.json, skip completed artifacts, proceed directly to next_artifact.

Repeat until the worker returns `## Layers Complete`.

### Phase 2 — UI Layer

Read `state.json` from the run directory. Check `completed_artifacts` against the UI layer rows in plan.md. Count UI artifacts with `status: create` or `status: exists` that are not yet in `completed_artifacts`.

**If zero pending UI artifacts → skip Phase 2 entirely and proceed to Step 6.**

Extract `stateholder_contract` path from state.json. Re-read `plan.md` and `context.md` from disk. Spawn `builder-ui-worker`:

> Pre-loaded context below — do not re-read plan.md, context.md, or state.json.
>
> **plan.md**
> \<content\>
>
> **context.md**
> \<content\>
>
> **Stateholder contract path:** \<stateholder_contract from state.json, or "none" if null\>
>
> \<if ## Figma Alignment section is present in context.md, include — otherwise omit\>
> **Figma Instruction:** For every Screen and Component artifact, before writing any code:
> 1. Look up the artifact in the `## Figma Alignment` table in context.md above to get its Figma Files list
> 2. `Read` each `.md` file — extract components, states, interactions, tokens, annotations
> 3. `Read` each `layout_file` JSX — full file, no truncation
> 4. `Read` each `screenshot` `.png` — mandatory, not optional; visual inspection required before implementing
>
> Proceed directly to the first pending UI artifact.

**Checkpoint loop:** if the worker returns `## Context Checkpoint` instead of `## Feature Complete`, immediately re-spawn a fresh `builder-ui-worker` without user interaction:

> Resuming from context checkpoint. Pre-loaded context below — do not re-read plan.md, context.md, or state.json.
>
> **plan.md**
> \<content — re-read from disk\>
>
> **context.md**
> \<content — re-read from disk\>
>
> **Stateholder contract path:** \<stateholder_contract from state.json\>
>
> **Resume from:** \<next_artifact from checkpoint block\>
> **State file:** \<state_file from checkpoint block\>
>
> \<if ## Figma Alignment section is present in context.md, include — otherwise omit\>
> **Figma Instruction:** (same as above)
>
> Read state.json, skip completed artifacts, proceed directly to next_artifact.

Repeat until the worker returns `## Feature Complete`.

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
