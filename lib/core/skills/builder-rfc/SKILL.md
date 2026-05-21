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
- Hold all fetched content inline — do not write to disk

### Step 3a — Figma Frame Drill-Down (mandatory when Figma URL is provided)

Never call `get_design_context` on a canvas or top-level file URL and accept a failure or sparse result as final.

1. Extract `fileKey` and `canvasNodeId` from the Figma URL (convert `-` to `:` in nodeId).
2. Call `mcp__Figma_MCP__get_design_context(fileKey, canvasNodeId, clientLanguages: dart, clientFrameworks: flutter)`.
3. **If the response is sparse / section-level** (child `<frame>` elements present, or note says "call get_design_context individually"):
   - Call `mcp__Figma_MCP__get_metadata(fileKey, canvasNodeId)` to get the full node tree.
   - From the tree, collect all instance nodes where `width ≤ 414` (mobile frame width).
   - Group by semantic name — e.g. "Select assignee", "Edit ticket", "Filter screen".
   - Pick the 2–3 most representative states per group (default, empty/error, variant).
   - Call `mcp__Figma_MCP__get_design_context` on each selected frame **in parallel**.
4. **If the response is a full design context** (JSX code returned): still call `get_metadata` to check for child frames — the provided node may contain multiple distinct screens.

From each `get_design_context` response, extract and record inline per frame:
- **components**: component names and Figma node IDs
- **tokens**: color hex values → MekariPixel candidate (`MpColors.*`), spacing values → `MpSpacing.*`, typography style names → `MpTypography.*`
- **controls**: interaction type per selectable row — checkbox / radio / chevron `>` / toggle / text link — inferred from screenshot and JSX
- **navigation**: flat list / two-level drill-down / modal / inline expansion — inferred from chevron presence and screen count

### Step 3b — Design System Component Resolution (mandatory for every UI-layer Epic)

For each unique component description found across all frames:

1. Query `mcp_mobile-qontak_search_design_system` (or `mcp_mobile-qontak2_search_design_system`) with the component description.
2. Also grep `features/qontak_component_lib/` for an existing widget implementation.
3. Classify each as `reuse-existing` (exact component/widget name) or `create-new` (reason why nothing matches).

Hold all frame data and component bindings inline as `figma_design_context`. Do not write to disk yet.

## Step 4 — Derive Planning Inputs

Inline — do not spawn an agent:

| Input | Rule |
|---|---|
| `feature` | Epic key + slugified summary, lowercased, hyphens. Example: `proj-123-user-profile` |
| `new-or-update` | `issuetype == Bug` or summary contains fix/update/change/modify → `update`; otherwise → `new` |
| `operations` | Scan AC + description for GET/list, GET/single, POST/create, PUT/update, DELETE. Default to all when ambiguous. |
| `separate-ui-layer` | Detect from labels/components (ios/android/flutter → `true`; web → `false`). Default `true`. |
| `platform` | Detect from labels, components, or project key prefix. If undetectable, call `AskUserQuestion` to resolve. |

## Step 4b — Mechanism Deep-Read (mandatory — runs before convergence loop)

**Rule: Never propose a new Domain or Data artifact based on PRD text alone. Always confirm from code that an existing mechanism cannot handle the requirement.**

From the Epic description and PRD, identify the domain objects involved (e.g., "team assignment", "filter by assignee", "ticket status change"). Then for each:

**1. Derive search terms — do NOT use hardcoded names.** From the Epic/PRD, identify the domain noun (e.g. "task", "contact", "deal"). Then:
- Grep for `*Type`, `*Kind`, or `*Category` enums associated with that noun — these indicate an existing type-dispatch mechanism
- Grep for any builder or factory method that returns `List<` + a typed entry for this domain — these indicate a shared pipeline
- Use the domain noun + action verb (`assign`, `filter`, `create`) as a seed

```
grep_search(
  query: "<DomainNoun>Type | <DomainNoun>Field | <DomainNoun>Builder | <feature-verb><DomainNoun>",
  includePattern: "features/<module>/lib/**/*.dart"
)
```

**2. Deep-read the mechanism** — for each match, read the full method body (not just the file name):
- Does the enum already have a case that covers the new capability?
- Does the builder/mapper iterate the enum generically, or does it require explicit new branches?
- Would adding a new enum constant be sufficient, or is a new artifact required?

**3. Search for similar interaction patterns** for BLoC behavior proposals:
- Grep for events with `Open`, `Navigate`, `Show`, `Push`, `Back` + the feature domain noun in the same BLoC
- Read the event class to document the established navigation pattern in this project

**4. Produce `mechanism_coverage`** — a table for each PRD capability:

| PRD Capability | Existing Mechanism Found | Coverage | Notes |
|---|---|---|---|
| Team assignment | `crmProperties` + `FieldType.assigneeWithTeam` | ✓ Covered | No new Domain/Data needed |
| New field X | (none found) | ✗ Not covered | New entity + use case required |

Also record `reference_bloc_patterns` — any existing BLoC patterns found for similar interactions.

Hold `mechanism_coverage` and `reference_bloc_patterns` inline.

### Covered-path enforcement (mandatory — apply before the convergence loop)

For every capability marked **✓ Covered** in `mechanism_coverage`:

1. **Convergence loop instruction** — when sending findings to the planners and orchestrator, prepend:
   > "The following capabilities are confirmed covered by existing mechanisms and MUST be excluded from Domain and Data proposals: `<list of covered capabilities>`. Do not propose new entity fields, new `@freezed` unions, or new `@JsonKey` model fields for these. Any Domain or Data artifact that would only serve a covered capability must be marked `Status: covered-by-existing`."

2. **Architecture section rule** — the RFC Architecture section for each covered capability MUST be written as:
   ```
   #### Domain — No changes needed
   Covered by existing `<mechanism name>`. No new entity fields required.

   #### Data — No changes needed
   Covered by existing `<mechanism name>`. No new model fields or mapper branches required.
   ```
   No Dart code blocks. No `@freezed` / `@JsonKey` field listings. One explanatory sentence only.

3. **API Contract rule** — the API Contract section for a covered capability MUST describe the **existing** payload format confirmed by the audit (e.g., the `crmProperties` array, the existing enum dispatch body). Do NOT derive new top-level request fields from PRD field names alone. If the existing mechanism is the only confirmed submission path, say so and raise an Open Question if backend confirmation is still needed.

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
> **Mechanism Coverage (from Step 4b):**
> <mechanism_coverage table>
> **Rule:** Do NOT propose new Domain or Data artifacts for any capability marked ✓ Covered above.
>
> **Reference BLoC Patterns (from Step 4b):**
> <reference_bloc_patterns — existing drill-down / navigation patterns found in the codebase>
> **Rule:** Match proposed BLoC events to the actual navigation model confirmed from Figma screenshots and existing patterns. Never invent event names from PRD text alone.
>
> **Figma Design Context (from Step 3a–3b):**
> <figma_design_context — per-frame: component names, token values, interaction controls, navigation model, component bindings (reuse vs create)>
> **Rule:** All UI ticket widget names, interaction controls, and navigation models must come from this context. Never describe UI from PRD text alone.

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

Create the output directory:

```bash
mkdir -p "$(git rev-parse --show-toplevel)/.claude/agentic-state/rfc"
```

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
> **Mechanism Coverage:**
> <mechanism_coverage table from Step 4b>
>
> **Figma Design Context:**
> <figma_design_context from Step 3a–3b — per-frame: components, tokens, controls, navigation, component bindings>
>
> **plan.md:**
> <content>
>
> **context.md:**
> <content>
>
> **Mandatory output rules for UI tickets:**
> 1. Every UI ticket MUST include a **Figma Design Context table**: screen state → Figma node ID → key observations (do not leave this absent).
> 2. Every UI ticket MUST include a **Design Corrections callout** if any PRD description contradicts Figma pixels — call it out explicitly.
> 3. Every UI ticket MUST include a **Design Tokens table**: colors / spacing / typography from Figma styles → MekariPixel mapping.
> 4. Every UI ticket MUST include a **Component Bindings table** — for every UI element: `reuse-existing` (exact widget name) OR `create-new` (reason). Never leave the source ambiguous.
> 5. Interaction model must be stated explicitly: checkbox / radio / chevron `>` / toggle / text link — verified from Figma, not inferred from PRD text.
> 6. Navigation model must be stated explicitly: flat list / two-level drill-down / modal / inline expansion — verified from Figma, not inferred from PRD text.

**Mandatory output rules for Domain/Data architecture (applies to every RFC):**
> 7. For every PRD capability with `✓ Covered` in Mechanism Coverage: the RFC Architecture → Domain and → Data sub-sections for that capability MUST be written as "No changes needed — covered by existing `<mechanism name>`." A single sentence is sufficient. **Never write `@freezed` class extensions, new entity fields, or `@JsonKey` model fields for a covered capability.**
> 8. The API Contract section for each capability MUST be derived from the **confirmed existing submission mechanism** found in the audit (e.g., the `crmProperties` array, an existing endpoint body). Do not invent new top-level request fields from PRD field-name descriptions alone. If the existing mechanism was confirmed but backend confirmation is still pending, state the assumption and raise it as an Open Question.
> 7. Never use a component name that was not found via Step 3b (design system query or `qontak_component_lib` grep). If creating a new widget, justify it.

Wait for `builder-rfc-writer` to complete. Report the output file paths to the user.
