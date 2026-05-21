---
name: builder-pres-resolve-design
description: Resolve UI element descriptions against the design system catalog using three-tier lookup (MekariPixel → shared component lib → new widget). Returns Design System Bindings, Shared Component Bindings, and Custom Widgets tables. Soft-fails with empty tables if no sources are available. Appends gaps to widget-debt.md.
user-invocable: false
tools: Grep, Read, Bash, mekari_pixel_query, mekari_pixel_get
---

## Input

| Parameter             | Description                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| `artifact_name`       | Name of the Screen or Component artifact from plan.md                                                     |
| `ui_description`      | UI elements to resolve — use Figma section content when available, otherwise plan.md artifact description |
| `current_feature_pkg` | (optional) Current feature package name e.g. `crm_note` — used for feature-local placement paths          |
| `platform`            | Platform identifier: `crm` or `chat` — controls which tiers are available                                 |

## Steps

### 1 — Parse keywords

Parse `ui_description` into individual keyword phrases (e.g. `"primary button, avatar, list tile"` → `["primary button", "avatar", "list tile"]`).

Maintain three buckets throughout: `tier1_matched`, `tier2_matched`, `unmatched`.

---

### 2 — Tier 1: MekariPixel

For each keyword:

**2a — MCP (primary):**

- Call `mekari_pixel_query(query=<keyword>, n_results=3)`
- From returned chunks: extract component name, description, key params
- If high-confidence match: record in `tier1_matched`
- If ambiguous or constructor params are insufficient: call `mekari_pixel_get(name="Mp<Name>")` for full doc
- If MCP unavailable or returns empty results: fall through to 2b

**2b — catalog.md Grep (fallback):**

- `find "$(git rev-parse --show-toplevel)/.claude/reference/design-system" -name "*catalog.md" 2>/dev/null | head -1`
- If catalog found: `Grep` for keyword (case-insensitive); `Read(offset=<line>, limit=8)` for each `### Mp<Name>` match
- If catalog also absent: mark keyword as unmatched and continue

---

### 3 — Tier 2: Shared component library (CRM only — skip for other platforms)

For each keyword still in `unmatched` after Tier 1 and `platform == "crm"`:

**3a — RAG query (primary):**

- Call `search_code("<keyword> widget", project_slug="crm")`
- If a matching widget class is returned: `Read` the class file (limit=30 lines from class declaration) to confirm purpose and key constructor params
- Record in `tier2_matched` if confirmed

**3b — Grep fallback:**

- If RAG unavailable or empty: `Grep` for keyword (case-insensitive) in `features/qontak_component_lib/lib/src/widgets/`
- For each match: `Read` the file at the match location (limit=30) to confirm the widget's purpose
- Record in `tier2_matched` if confirmed

---

### 4 — Tier 3: Scope decision for new widgets

For each keyword still `unmatched` after Tier 1 and Tier 2:

Answer: _"Will this widget be used across more than one feature module, or only within the current feature?"_

- If the widget concept is generic (reusable across features) → `cross-feature`
- If the widget is tightly specific to this screen's domain → `feature-local`

When in doubt, default to `cross-feature` — it is easier to move inward later than to promote outward.

Placement:

- `cross-feature` (CRM) → `features/qontak_component_lib/lib/src/widgets/{atoms|components}/`
- `cross-feature` (Chat) → `features/<current_feature_pkg>/lib/src/presentation/widgets/` _(Chat has no shared lib)_
- `feature-local` → `features/<current_feature_pkg>/lib/src/presentation/widgets/`

---

### 5 — Output

Return up to three tables. Omit any table with no rows.

```
## Design System Bindings

| UI element | Symbol | Variants | Import |
|---|---|---|---|
| <keyword> | `Mp<Name>` | <variants or —> | `package:mekari_pixel/mekari_pixel.dart` |

## Shared Component Bindings

| UI element | Symbol | Import |
|---|---|---|
| <keyword> | `QontakXxx` | `package:qontak_component_lib/qontak_component_lib.dart` |

## Custom Widgets

| UI element | Reason | Scope | Placement |
|---|---|---|---|
| <keyword> | no existing match | cross-feature | features/qontak_component_lib/lib/src/widgets/components/ |
| <keyword> | no existing match | feature-local  | features/<current_feature_pkg>/lib/src/presentation/widgets/ |
```

`## Design System Bindings` and `## Shared Component Bindings` entries are **hard constraints** for the creation skill — use exactly the symbol listed.
`## Custom Widgets` `Placement` is a **hard constraint** — the creation skill must place the new file at that path.

If all three tables are empty: `no UI elements resolved — check ui_description input`

---

### 6 — Widget debt log (non-blocking)

After completing all tiers, for each keyword that was NOT matched in Tier 1 (i.e. absent from MekariPixel):

> Check if `.claude/feedback/widget-debt.md` exists. If absent, skip silently.
> Before appending: `Grep` widget-debt.md for the same keyword + current date — skip if identical entry already exists.
> Append after `<!-- gap-entries: agent appends below this line -->`:

```markdown
### <YYYY-MM-DD> · `<current_feature_pkg>` — <keyword>

- **Requirement:** <requirement from ui_description context>
- **Figma:** <Figma link from Figma worker context, or "not provided">
- **Closest in mekari_pixel:** <nearest Tier 1 result, or "none found">
- **Closest in qontak_component_lib:** <nearest Tier 2 result, or "none found" / "N/A for this platform">
- **Suggested pixel contribution:** <brief suggestion based on the requirement>
- **Created by:** builder-pres-resolve-design
- **Status:** `open`
```

Do not log Tier 2 matches — if resolved in `qontak_component_lib`, it is not a design system gap.
Failure to write must never block or error the skill.
