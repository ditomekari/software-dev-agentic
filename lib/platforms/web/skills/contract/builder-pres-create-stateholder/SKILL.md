---
name: builder-pres-create-stateholder
description: Create a StateHolder for a feature — either a hook (client-side) or a pure function (server-side). Called by presentation-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create a ViewModel for a feature. First determine which pattern applies:

**Pattern A — Hook (`use*ViewModel`)** — when the component is a Client Component:
- Needs live data fetching, caching, or background refetch → TanStack Query
- Mutation-heavy, full-stack DB → Server Actions + `useState`
- Output file: `src/presentation/features/[feature]/use[Feature]ViewModel.ts`

**Pattern B — Pure function (`build*ViewModel`)** — when the page is a Server Component:
- Data fetched server-side in `async page.tsx`, no hooks needed
- Computes derived fields from domain entities (e.g., `isHiring`, `featuredJobs`)
- Output file: `src/presentation/features/[feature]/build[Feature]ViewModel.ts`

**Preconditions:**
- File must NOT exist — fail fast if it does
- Use case(s) must exist in `src/domain/use-cases/[feature]/`
- Check `Glob: src/presentation/features/*/` — read one existing ViewModel to match style

**Rules (both patterns):**
- No business logic — only state management (hook) or pure data transformation (pure fn)
- Return / output only serializable plain objects — no class instances
- Pattern B: zero hooks, zero async, zero side effects — pure input → output

**Pattern:** `reference/code-architecture/presentation-impl.md` — Grep `## ViewModel Hook` (hook), `## Server-Side ViewModel (Pure Function)` (pure function)

**Return:** created file path and which pattern was used. Suggest next step: `pres-create-screen`.
