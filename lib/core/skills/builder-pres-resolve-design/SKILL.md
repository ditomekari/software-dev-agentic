---
name: builder-pres-resolve-design
description: Resolve UI element descriptions against the MekariPixel catalog and return a Design System Bindings table. Called by builder-feature-worker before pres-create-screen and pres-create-component. Soft-fails with an empty table if the catalog is not present.
user-invocable: false
---

## Input

| Parameter | Description |
|---|---|
| `artifact_name` | Name of the Screen or Component artifact from plan.md |
| `ui_description` | Free-text description of UI elements in this artifact (from plan.md artifact notes or description) |

## Steps

### 1 — Check for catalog

```bash
find "$(git rev-parse --show-toplevel)/.claude/reference/design-system" -name "*catalog.md" 2>/dev/null | head -1
```

If no file is found — **soft fail**: return the output block with an empty table and note `catalog not found — place a catalog.md in .claude/reference/design-system/`.

Set `<catalog_path>` to the found file.

### 2 — Match each UI element

Parse `ui_description` into individual keyword phrases (e.g. `"primary button, avatar, list tile"` → `["primary button", "avatar", "list tile"]`).

For each keyword, `section-query` the catalog:
- `Grep` for the keyword (case-insensitive) in `<catalog_path>`
- For each matching `### Mp<Name>` heading: `Read(offset=<line>, limit=8)` to get description and key params
- Select the best match based on the description

### 3 — Output

Return exactly:

```
## Design System Bindings

| UI element | Symbol | Import |
|---|---|---|
| <keyword> | `Mp<Name>` | `package:mekari_pixel/mekari_pixel.dart` |
```

Omit rows where no match was found. If the table has no rows, add:
`| — | no matches | check catalog or use Material fallback |`
