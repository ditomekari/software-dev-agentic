---
name: builder-pres-resolve-design
description: Resolve UI element descriptions against the design system catalog. Returns a Design System Bindings table (matched) and a Custom Widgets table (unmatched). Soft-fails with empty tables if the catalog is not present.
user-invocable: false
---

## Input

| Parameter | Description |
|---|---|
| `artifact_name` | Name of the Screen or Component artifact from plan.md |
| `ui_description` | UI elements to resolve — use Figma section content when available, otherwise plan.md artifact description |

## Steps

### 1 — Check for catalog

```bash
find "$(git rev-parse --show-toplevel)/.claude/reference/design-system" -name "*catalog.md" 2>/dev/null | head -1
```

If no file is found — **soft fail**: return empty tables with note `catalog not found — place a catalog.md in .claude/reference/design-system/`.

Set `<catalog_path>` to the found file.

### 2 — Match each UI element

Parse `ui_description` into individual keyword phrases (e.g. `"primary button, avatar, list tile"` → `["primary button", "avatar", "list tile"]`).

For each keyword, `section-query` the catalog:
- `Grep` for the keyword (case-insensitive) in `<catalog_path>`
- For each matching `### Mp<Name>` heading: `Read(offset=<line>, limit=8)` to get description, key params, and variants
- Select the best match based on description; if no match found, mark as unmatched

### 3 — Source fallback (on-demand)

If a matched entry's key params are insufficient for the creation skill (e.g., a variant is referenced but its constructor is unclear), resolve the source path:
- `Grep` for `mekari_pixel:` in `pubspec.lock` to find the pub-cache hash
- Construct path: `~/.pub-cache/git/mekari-pixel-<hash>/mekari-pixel/lib/src/<widget_file>.dart`
- `Grep` for the class name → `Read(offset=<line>, limit=60)` to capture the full constructor

Include source path in the binding row only when used.

### 4 — Output

Return exactly:

```
## Design System Bindings

| UI element | Symbol | Variants | Import |
|---|---|---|---|
| <keyword> | `Mp<Name>` | <variant list or —> | `package:mekari_pixel/mekari_pixel.dart` |

## Custom Widgets

| UI element | Reason | Action |
|---|---|---|
| <keyword> | no catalog match | create custom widget |
```

Omit a table entirely if it has no rows. If both tables are empty, add a single note:
`no UI elements resolved — check ui_description input`
