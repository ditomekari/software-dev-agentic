---
name: builder-test-create-presentation
description: Write tests for ViewModel hooks and View components. Called by builder-test-worker.
user-invocable: false
tools: Read, Write, Glob
---

Write tests for a presentation layer file.

**Preconditions:**
- Read the target file: identify whether it's a hook (`use*`) or pure function (`build*`)
- Check `__tests__/utils/queryClientWrapper.tsx` exists — required for hook tests only
- Output location:
  - Hook → `__tests__/presentation/hooks/use[Feature]ViewModel.test.ts`
  - Pure function → `__tests__/presentation/view-models/build[Feature]ViewModel.test.ts`
  - View component → `__tests__/presentation/[Feature]View.test.tsx`

**`use*ViewModel` hook test rules:**
- Use `renderHook` + `QueryClientWrapper` from `__tests__/utils/queryClientWrapper.tsx`
- Mock use case(s) via `test-create-mock`
- Cover state transitions: initial loading → loaded → error
- For mutations: cover success path + error path

**`build*ViewModel` pure function test rules:**
- No React utilities needed — it's a plain function
- Pass mock domain entities directly as input
- Assert every derived field is computed correctly
- Cover all branching conditions (e.g., `isHiring: false` when `siteStatus !== 'active'`)
- 100% branch coverage target (same as domain services)

**View component test rules:**
- Use React Testing Library (`render`, `screen`, `userEvent`)
- For hook-pattern views: mock the ViewModel hook (`vi.mock`)
- For pure-fn views: pass a pre-built `viewModel` prop directly — no mocking needed
- Cover each render state: loading, error, data

**Pattern:** `reference/code-architecture/testing-impl.md` — Grep `## Presenter Tests` · `reference/code-architecture/presentation-impl.md` — Grep `## Server-Side ViewModel (Pure Function)`

**Return:** created test file path.
