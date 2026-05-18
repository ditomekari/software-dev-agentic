---
name: builder-pres-create-screen
description: Create a View component and App Router page. Handles both Client Component (hook pattern) and Server Component (build*ViewModel pattern). Called by builder-ui-worker.
user-invocable: false
tools: Read, Write, Edit, Glob
---

Create the View component and App Router page. Pattern depends on which ViewModel was created.

**Determine pattern from the ViewModel file:**
- `use*ViewModel.ts` exists → **Client Component path**
- `build*ViewModel.ts` exists → **Server Component path**

---

**Client Component path:**
- `src/presentation/features/[feature]/[Feature]View.tsx` — `'use client'`, calls `useDI()` + hook
- `src/app/[route]/page.tsx` — Server Component, renders `<[Feature]View />`

**Server Component path:**
- `src/presentation/features/[feature]/[Feature]View.tsx` — receives `viewModel` as prop. Add `'use client'` only if the view has interactivity (event handlers, modals, etc.)
- `src/app/[route]/page.tsx` — `async` Server Component, fetches data → `build*ViewModel()` → passes result as prop

---

**Preconditions:**
- ViewModel file must exist — run `pres-create-stateholder` first if missing
- Check `Glob: src/presentation/features/*/[A-Z]*View.tsx` — read one to match style

**Rules (both paths):**
- Views render — no business logic
- Atoms/molecules → `src/presentation/common/` — primitive props only
- Organisms → `[feature]/organisms/` — accept entities as props, never call `useDI()`
- Only Client Component Views call `useDI()`
- `async page.tsx` props must be serializable (no `Date` instances, no class instances)

**Route constant:** add to `src/presentation/navigation/routes.ts`

**Pattern:** `reference/code-architecture/presentation-impl.md` — Grep `## React Component (View)`, `## Server-Side ViewModel (Pure Function)` · `reference/code-architecture/navigation-impl.md` — Grep `## Route Constants` · `reference/ssr.md` — Grep `## Presentation Layer — Mostly Client`

**Return:** created file paths.
