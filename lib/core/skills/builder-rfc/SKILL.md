---
name: builder-rfc
description: Generate an RFC and ticket breakdown from a Jira Epic + PRD + optional Design. Fetches inputs, runs the Clean Architecture convergence planning loop, then writes <epic-slug>-rfc.md and <epic-slug>-breakdown.md.
user-invocable: true
allowed-tools: Bash, Read, AskUserQuestion, Agent
---

## Arguments

`$ARGUMENTS` — Jira Epic key (optional). Example: `PROJ-123`.

## Step 1 — Resolve Jira Input

If `$ARGUMENTS` is empty, call `AskUserQuestion`:

```
question    : "Which Jira Epic should this RFC be based on?"
header      : "Epic"
multiSelect : false
options     :
  - label: "Enter Epic key", description: "e.g. PROJ-123"
```

Use the provided value as `<epic-key>`.

## Step 2 — Fetch Epic

Use the available Jira MCP tool. Prefer in order: `getJiraIssue`, `mmpa_get_jira`.

If neither is available, stop with a clear message.

Extract:
- `summary` — ticket title
- `description` — full body
- `issuetype`, `labels`, `components`
- Acceptance criteria — look for `## AC`, `## Acceptance Criteria`, or `h2. AC` sections

## Step 3 — Fetch PRD and Design

Call `AskUserQuestion` (batch both questions):

```
question    : "Provide the PRD Confluence URL for this Epic."
header      : "PRD"
multiSelect : false
options     :
  - label: "Paste URL", description: "Confluence page URL"
  - label: "No PRD — use Epic description only", description: "Skip Confluence fetch"

question    : "Is there a Figma design for this Epic?"
header      : "Design"
multiSelect : false
options     :
  - label: "Yes — paste Figma URL", description: "Design will be included in RFC context"
  - label: "No design", description: "Skip design input"
```

- If PRD URL provided → fetch via `mmpa_get_confluence_page`, read staging file, extract `.content`
- If Figma URL provided → fetch via `mcp__Figma__get_figma_data`
- Hold all fetched content inline — do not write to disk

## Step 4 — Derive Planning Inputs

Inline — do not spawn an agent:

| Input | Rule |
|---|---|
| `feature` | Epic key + slugified summary, lowercased, hyphens. Example: `proj-123-user-profile` |
| `new-or-update` | `issuetype == Bug` or summary contains fix/update/change/modify → `update`; otherwise → `new` |
| `operations` | Scan AC + description for GET/list, GET/single, POST/create, PUT/update, DELETE. Default to all when ambiguous. |
| `separate-ui-layer` | Detect from labels/components (ios/android/flutter → `true`; web → `false`). Default `true`. |
| `platform` | Detect from labels, components, or project key prefix. If undetectable, call `AskUserQuestion` to resolve. |

## Step 5 — Gather Intent (Non-Interactive)

Spawn `builder-feature-orchestrator` with mode `gather-intent-prefilled`:

> **Mode: gather-intent-prefilled**
>
> **Pre-filled intent (do not ask for any of these):**
> - feature: `<derived feature name>`
> - new-or-update: `<new|update>`
> - operations: `<comma-separated list>`
> - separate-ui-layer: `<true|false>`
> - platform: `<platform>`
>
> **Epic context:**
> <epic summary + description + AC>
>
> **PRD context:**
> <prd content, or "None — use Epic description only.">
>
> **Design context:**
> <figma content, or "None provided.">

Wait for `Decision: spawn-planners`. Initialize:
- `visited` = []
- `all_findings` = []
- `round` = 1

## Step 6 — Planning Convergence Loop

Repeat until the orchestrator returns `Decision: converged` or `Decision: blocked`.

### 6a — Spawn planners for this round

From the current `Decision: spawn-planners` block, spawn each listed planner **in parallel**:

- `builder-domain-planner` — if `domain` in spawn list
- `builder-data-planner` — if `data` in spawn list
- `builder-pres-planner` — if `pres` in spawn list
- `builder-app-planner` — if `app` in spawn list

Pass to each planner: feature name, platform, module-path (from orchestrator output).

Wait for all planners to complete. Add spawned layers to `visited`. Append findings to `all_findings`.

### 6b — Send findings to orchestrator

Spawn `builder-feature-orchestrator` with mode `process-findings`:

> **Mode: process-findings**
>
> Round: <N>
> Visited layers: <comma-separated>
>
> **Accumulated Findings:**
> <all_findings content>

- **`Decision: spawn-planners`** → increment `round`, go to 6a
- **`Decision: converged`** → proceed to Step 7
- **`Decision: blocked`** → call `AskUserQuestion` with the orchestrator's question and options, send the answer back as a follow-up `process-findings` call, re-evaluate

**Max rounds guard:** If `round` reaches 4 without convergence, surface to the user:
> "RFC planning could not converge after 3 rounds. Open questions: <list from last blocked decision>. Please clarify and retry."

Stop.

## Step 7 — Synthesize Plan

Spawn `builder-feature-orchestrator` with mode `synthesize`:

> **Mode: synthesize**
>
> Non-interactive — auto-approve after writing plan.md and context.md.
>
> **All Accumulated Findings:**
> <all_findings content>

Wait for the orchestrator to write `plan.md` + `context.md` and return the plan summary.

## Step 8 — Write RFC and Breakdown

Read `plan.md` and `context.md` from the run directory. Then spawn `builder-rfc-writer`:

> **Epic key:** <epic-key>
> **Epic slug:** <feature>
>
> **Epic content:**
> <summary + description + AC>
>
> **PRD content:**
> <prd content or "None">
>
> **Design content:**
> <figma content or "None">
>
> **plan.md:**
> <content>
>
> **context.md:**
> <content>

Wait for `builder-rfc-writer` to complete. Report the output file paths to the user.
