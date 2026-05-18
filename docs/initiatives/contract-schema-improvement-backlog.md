> Author: Puras Handharmahua · 2026-04-19
> Status: Backlog — pending platform file alignment before each item can be registered in `docs/contract/builder-auditor-schema.md`

# Contract Schema — Convention Improvement Backlog

Gaps identified by comparing `docs/contract/builder-auditor-schema.md` against CLEAN Architecture, SOLID, and DRY theory. Each item below was confirmed **not yet safe to register** because one or more platform contract files are missing the required `##` heading.

Adding a keyword to `docs/contract/builder-auditor-schema.md` before the platform files are updated causes immediate `arch-check-conventions` violations. The correct sequence is:

```
1. Add ## heading to all 3 platform contract files (web, iOS, flutter)
2. Register the keyword in docs/contract/builder-auditor-schema.md
3. Update the core template if not already covered
```

---

## presentation.md — Input / Output contract gaps

**Theory basis:** CLEAN Architecture's Presentation layer has three distinct contracts:
- **State** — persistent output snapshot (already registered ✅)
- **Events / Input** — user intentions flowing into the StateHolder (input port)
- **Actions / Output** — one-time side effects after processing an event (navigation, toasts, dialogs)

The current schema captures only the output snapshot. Input and side effects are unregistered, meaning platform files have no obligation to document them.

### Gap 1 — `Events / Input` (input port)

Current platform headings:

| Platform | Heading | Has "Events" substring? |
|---|---|---|
| web | *(none)* | ❌ |
| iOS | *(none)* | ❌ |
| flutter | `## Events` | ✅ |

**Required before registering:** Add `## Events` (or a heading containing "Events") to web and iOS platform `presentation.md`.

**SOLID relevance:** ISP — the input and output sides of the StateHolder are separate interfaces; collapsing them into `State` only obscures the contract.

---

### Gap 2 — `Actions / Output` (side effects)

Current platform headings:

| Platform | Heading | Has "Actions" or "Side Effects" substring? |
|---|---|---|
| web | *(none)* | ❌ |
| iOS | *(none)* | ❌ |
| flutter | `## BlocListener (Side Effects)` | "Side Effects" ✅, "Actions" ❌ |

**Required before registering:** Decide on a canonical keyword — `Actions` or `Side Effects` — then add a matching `##` heading to all 3 platform files. Flutter already covers the concept under `BlocListener`; the heading may need a rename or alias.

**CLEAN relevance:** One-time side effects are architecturally distinct from persistent State. Conflating them is a common source of navigation bugs.

---

## testing.md — Naming divergence blocks keyword registration

**Theory basis:** Use Cases are the primary test target in CLEAN Architecture. They contain all business rules and should be the most-tested layer. Neither `Use Cases` nor a common synonym is currently a required keyword.

Current platform headings:

| Platform | Heading | Concept |
|---|---|---|
| web | `## Service Tests` | Tests domain services + use case logic |
| iOS | `## Service Tests` | Tests domain services |
| flutter | `## Use Case Tests` | Tests use cases directly |

The naming divergence (`Service Tests` vs `Use Case Tests`) is a normalization problem that needs resolution before a keyword can be registered without breaking one platform.

**Required before registering:** Align platform files — either rename web/iOS `## Service Tests` to include "Use Case" (e.g. `## Use Case and Service Tests`) so a `Use Case` keyword substring works across all three, or adopt a broader keyword that covers both.

**Note:** `flutter` also has `## BLoC Tests` for presentation-layer testing. Web has `## ViewModel Hook Tests`. iOS has `## ViewModel Tests`. A `StateHolder Tests` keyword (or platform-specific alias) could register this cross-platform concern once naming is aligned.

---

## di.md — Scope and registration order not documented in platform files

**Theory basis:** DI correctness depends on two things beyond principles: (1) knowing which scope to assign each dependency, (2) registering in dependency-graph order.

### Gap 3 — `Scope Rules`

Current platform headings — none of the 3 platforms have a `##` heading covering scope assignment:

| Platform | Closest heading | Gap |
|---|---|---|
| web | `## Decision Rule` | Covers server vs client container choice, not singleton/transient/feature-scoped |
| iOS | `## When to Use What?` | Partially covers scope, but heading doesn't contain a registerable keyword |
| flutter | `## Registering Classes` | Shows `registerSingleton` / `registerFactory` syntax but no explicit rules section |

**Required before registering:** Add a `## Scope Rules` (or `## Scopes`) section to all 3 platform files documenting which scope applies to each artifact type (StateHolder → feature-scoped, HTTP client → singleton, mapper → transient).

**SOLID relevance:** "Container owns lifecycle" is DI Principle 4 — but without a Scope Rules section, agents and engineers have no greppable guidance on which lifecycle to use.

---

### Gap 4 — `Registration Order`

None of the 3 platform `di.md` files have a `## Registration Order` heading. The concept is covered in the core template (`lib/core/reference/code-architecture/di.md`) but never surfaced in platform files.

**Required before registering:** Add a `## Registration Order` section to all 3 platform files showing the correct dependency-graph sequence for that platform's DI framework.

**Lower priority than Scope Rules** — registration order errors surface immediately at runtime; scope errors surface subtly later.

---

## Completed (for reference)

| Keyword | File | Added | Note |
|---|---|---|---|
| `Services` | `domain.md` | 2026-04-19 | Substring of `## Services` (web/iOS) and `## Domain Services` (flutter) — zero platform changes needed |
