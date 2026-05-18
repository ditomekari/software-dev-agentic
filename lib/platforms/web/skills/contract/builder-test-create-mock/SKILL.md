---
name: builder-test-create-mock
description: Scaffold a Mock class for any interface, using vi.fn() for every method. Called by builder-test-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create `__tests__/mocks/Mock[InterfaceName].ts`.

**Preconditions:**
- Check `Glob: __tests__/mocks/Mock[InterfaceName].ts` — if it exists, update it rather than create a new file
- Read the interface file to extract every method signature

**Rules:**
- Class name: `Mock[InterfaceName]` — always `Mock` prefix, never `Impl` suffix
- `implements [InterfaceName]` — TypeScript enforces completeness
- Every method → one `vi.fn()` property typed with `Parameters<...>` and `ReturnType<...>`
- No logic — mocks are pure stubs
- If test framework is Jest: use `jest.fn()` from `@jest/globals`

**Pattern:** `reference/code-architecture/testing-impl.md` — Grep `## Presenter Tests`

**Return:** created/updated file path and a minimal usage example.
