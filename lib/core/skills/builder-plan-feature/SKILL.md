---
name: builder-plan-feature
description: Plan then build a feature — optionally resolves external inputs (Jira, PRD, Figma, local .md), gathers intent via builder-feature-orchestrator, runs the convergence planning loop (spawning only the needed layer planners per round), shows an interactive approval prompt, then executes with builder-feature-worker (Domain/Data/Pres/App) followed by builder-ui-worker (UI layer) on approval.
user-invocable: true
allowed-tools: Agent, AskUserQuestion, Bash, Read, WebFetch
---

## Step 0A — Input Gate (always first)

Read the user's message. Classify intent:

**Verification / review intent** — triggered when the message contains any of: `verify`, `check`, `review`, `read the code`, `look at the code`, `test`, `confirm`, `validate`, `what was built`, `is it correct`, or similar phrases asking to inspect existing work.

→ **Do not read any source files, run any tests, or do any codebase exploration.**
→ Run the Preflight bash commands to find existing runs. Derive `run_dir`. Proceed directly to **Step R** — the orchestrator will gather the user's concerns as `open_questions` and route them to planners.
→ The user's full message is the intent. Pass it verbatim to the orchestrator in Step R1. Do not act on it yourself.

**New feature / planning intent** — no verification keywords → proceed to Preflight normally.

## Preflight — Check Existing Runs

Before resolving any inputs, check for existing runs — both completed plans and partial-planning runs interrupted before synthesis:

```bash
find "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs" -maxdepth 2 -name "plan.md" 2>/dev/null
find "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs" -maxdepth 2 -name "figma-groups.json" 2>/dev/null
```

If neither found → proceed to Step 0.

**Partial-planning run detected** — if `figma-groups.json` exists in a run dir but no `plan.md` alongside it:
- Set `run_dir` to the parent directory of the found `figma-groups.json`
- Read `figma-groups.json` to restore `figma_groups`
- Read all `findings-round-*.json` files in that run dir (sorted by round number) to restore `all_findings` and determine last completed `round`
- Reconstruct `visited` from the union of all `findings-round-*.json` `visited` arrays
- Call `AskUserQuestion`:

```
question    : "A planning session was interrupted before the plan was written. Resume it?"
header      : "Resume Planning"
multiSelect : false
options     :
  - label: "Resume", description: "Restore figma groups and planner findings, re-enter the planning loop"
  - label: "Discard", description: "Delete the partial run and start fresh"
```

**Resume** → skip Steps 0–1.5b, set `round = <last completed round> + 1`, re-enter Step 2 with restored state.
**Discard** → `rm -rf "<run_dir>"`, proceed to Step 0.

If only `plan.md` found → call `AskUserQuestion`:

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

1. Derive `run_dir` from the path of the selected `plan.md` — take its parent directory. Do not reconstruct from feature name.
2. **Do NOT read any source code or implementation files — even if the user's message asks to verify or review code.** Pass verification concerns to the orchestrator as open questions; planners own all codebase exploration.
3. Proceed directly to **Step R**.

## Step R — Review and Adjust (Resume path only)

**Scope boundary:** this skill does not read source code or implementation files at any point in Step R. Only the shell commands explicitly listed below are permitted. All codebase exploration is delegated to the orchestrator and planners.

### Step R0 — Figma repair pre-check

```bash
find "<run_dir>/inputs" -name "figma-*.md" 2>/dev/null | sort
ls "<run_dir>/figma-groups.json" 2>/dev/null
```

**If figma-*.md files exist:**
- Check each file's `screenshot:` frontmatter. For any value starting with `http` where no corresponding `.png` exists on disk:
  ```bash
  curl -sL "<url>" -o "<run_dir>/inputs/figma-<slug>-screenshot.png"
  ```
  Then update the `screenshot:` frontmatter in that `.md` to the local path. Add `screenshot_url: <url>` if absent.
- If `figma-groups.json` is missing: read `parent_frame` frontmatter from every `figma-*.md` file and reconstruct it:
  ```bash
  cat > "<run_dir>/figma-groups.json" << 'EOF'
  <reconstructed JSON grouped by parent_frame>
  EOF
  ```

**Restore figma_groups:** if `figma-groups.json` now exists (found or just written), read it and store as `figma_groups` for use in Step 2.

### Step R1 — Gather intent

Spawn `builder-feature-orchestrator` with mode `review-resume`:

> **Mode: review-resume**
>
> **run_dir:** \<run_dir\>

Wait for the orchestrator's decision block:

- **`Decision: resume-as-is`** → proceed directly to Step 5 (Execute). No planning needed.

- **`Decision: spawn-planners`** → extract from the decision block:
  - `feature`, `platform`, `module_path` (used in Step 2)
  - `completed_artifacts` list
  - `open_questions` list (the user's stated issues — passed to planners)
  - Initialize: `visited = []`, `all_findings = []`, `round = 1`, `update_mode = true`
  - **Do NOT read any project files, search the codebase, or analyze artifacts here.** Planners own all artifact exploration — proceed immediately to Step 2.

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
> <if resolved_inputs or pending_figma_urls is non-empty, include the following block — otherwise omit>
> **Resolved Inputs:**
> <for each non-Figma item: "### <type> — <source>\n<content>">
> <if pending_figma_urls is non-empty: "### Figma designs (pending fetch)\n<list each URL — will be fetched after feature name is confirmed>">
>
> Ask the user for feature intent. Return a `Decision: spawn-planners` block when done.

Wait for the orchestrator to return. Extract the `Decision: spawn-planners` block. Note the `feature` name from the orchestrator output.

Initialize:
- `visited` = [] (empty set of explored layers)
- `all_findings` = [] (accumulated planner findings across all rounds)
- `round` = 1

## Step 1.5 — Fetch Figma Inputs (skip if `pending_figma_urls` is empty)

Now that `feature` is known, resolve the run directory:

```bash
echo "$(git rev-parse --show-toplevel)/.claude/agentic-state/runs/<feature>"
```

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
