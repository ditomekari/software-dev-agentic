---
name: builder-plan-feature
description: Plan then build a feature — optionally resolves external inputs (Jira, PRD, Figma, local .md), gathers intent via builder-feature-orchestrator, runs the convergence planning loop (spawning only the needed layer planners per round), shows an interactive approval prompt, then executes with builder-feature-worker on approval.
user-invocable: true
allowed-tools: Agent, AskUserQuestion, Bash, Read, WebFetch
---

## Preflight — Check Existing Runs

Before resolving any inputs, check for existing runs:

```bash
find "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs" -maxdepth 2 -name "plan.md" 2>/dev/null
```

If none found → proceed to Step 0.

If found → call `AskUserQuestion`:

```
question    : "Existing plans found in runs/. What would you like to do?"
header      : "Resume or Start"
multiSelect : false
options     :
  - label: "Continue existing", description: "Pick an existing plan to review and resume"
  - label: "Start fresh",       description: "Plan and build a new feature from scratch"
```

**Start fresh** → proceed to Step 0.

**Continue existing** → read the `feature` name and `status` from the frontmatter of each found `plan.md`. Also read `state.json` alongside each plan to get `completed_artifacts` count. Call `AskUserQuestion` with one option per run (up to 4):

```
question    : "Which plan would you like to resume?"
header      : "Existing Plans"
multiSelect : false
options     : one per found plan — label: <feature>, description: "<completed count> artifacts done · status: <status>"
```

After the user selects a run:

1. Read `plan.md`, `context.md`, and `state.json` from the selected run directory.
2. Proceed to **Step R — Review and Adjust**, then continue to Step 4.

## Step R — Review and Adjust (Resume path only)

Spawn `builder-feature-orchestrator` with mode `review-resume`:

> **Mode: review-resume**
>
> **plan.md**
> \<content\>
>
> **context.md**
> \<content\>
>
> **Completed artifacts:** \<comma-separated list from state.json completed_artifacts, or "none"\>

Wait for the orchestrator's decision block:

- **`Decision: resume-as-is`** → proceed to Step 4 using the existing plan.md and context.md.
- **`Decision: resume-updated`** → archive the current files before writing the updated content:

  ```bash
  # Determine next version number
  N=$(ls "<run_dir>/plan-v"*.md 2>/dev/null | wc -l | tr -d ' ')
  N=$((N + 1))
  mv "<run_dir>/plan.md"    "<run_dir>/plan-v${N}.md"
  mv "<run_dir>/context.md" "<run_dir>/context-v${N}.md"
  ```

  Then write the updated `plan.md` and `context.md` from the orchestrator's response. The worker always reads `plan.md` as the active plan; prior versions are preserved as `plan-v1.md`, `plan-v2.md`, etc. Proceed to Step 4.

## Step 0 — Resolve Inputs

Parse all arguments passed to this skill. Classify each by pattern:

| Pattern | Type | Fetch via |
|---|---|---|
| URL containing `jira` or `atlassian`, or bare ticket ID (e.g. `PROJ-123`) | Jira ticket | Atlassian MCP tool (attempt; failure = not configured) |
| URL containing `figma.com` | Figma design | Spawn `builder-figma-worker` (isolated context; failure = not configured or fetch error) |
| Any other URL | PRD / doc | `WebFetch` |
| Path ending in `.md` | Local file | `Read` |

If no arguments are provided, skip this step — proceed to Step 1 with `resolved_inputs = []`.

Resolve the run directory path before fetching:
```bash
echo "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs/<feature>"
```

For Figma inputs, spawn one `builder-figma-worker` per URL — pass `figma_url`, `feature`, and `run_dir`. Spawn all Figma workers in parallel if multiple. For all other input types, fetch inline.

Attempt all fetches (inline + spawned workers) in parallel. Collect:
- `resolved_inputs` — successfully fetched items:
  - Non-Figma: `{ type, source, content }`
  - Figma: `{ type, source, summary, file }` — `summary` is the worker's `## Figma Worker Output` block; `file` is the written `.md` path
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

### Step 0b — Verify Figma Grouping (skip if no Figma inputs were resolved)

From the collected Figma worker outputs, group by `parent_frame`:

```
<parent_frame A> → [{ state, file }, { state, file }, ...]
<parent_frame B> → [{ state, file }, ...]
```

Call `AskUserQuestion`:

```
question    : "Figma frames detected. We grouped them into screens based on their parent frame in Figma.
               Does this look correct?

               <for each group:>
               • <parent_frame> — states: <comma-separated state names>
               "
header      : "Figma Screens"
multiSelect : false
options     :
  - label: "Correct",  description: "Grouping looks right — proceed to planning"
  - label: "Adjust",   description: "The grouping needs changes before we continue"
```

**Correct** → store as `figma_groups` and proceed.

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

## Step 1 — Gather Intent

Spawn `builder-feature-orchestrator` with mode `gather-intent`:

> **Mode: gather-intent**
>
> <if resolved_inputs is non-empty, include the following block — otherwise omit>
> **Resolved Inputs:**
> <for each non-Figma item: "### <type> — <source>\n<content>">
> <for each Figma item: paste the `## Figma Worker Output` summary block — do NOT inline file contents>
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

For `builder-pres-planner` specifically — if `figma_groups` was established in Step 0b, also pass:
- The full `figma_groups` structure (screen → states + file paths) — do NOT inline file contents

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
> <if Figma inputs were resolved in Step 0, include — otherwise omit>
> **Figma Reference Files:**
> <list each file path from resolved Figma inputs>
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
