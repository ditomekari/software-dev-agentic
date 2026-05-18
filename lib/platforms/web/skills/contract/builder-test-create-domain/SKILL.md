---
name: builder-test-create-domain
description: Write unit tests for domain layer files — use cases and domain services. Called by builder-test-worker.
user-invocable: false
tools: Read, Write, Glob
---

Write unit tests for a domain layer file.

**Preconditions:**
- Read the target file: extract class name, constructor params, and all public methods
- Check `__tests__/mocks/` for existing mocks — create missing ones via `test-create-mock` first
- Output location:
  - Use case → `__tests__/domain/use-cases/[Verb][Feature]UseCase.test.ts`
  - Service → `__tests__/domain/services/[Name]Service.test.ts`

**Use case test rules:**
- Mock the repository — never instantiate the real one
- Cover: happy path, error propagation (repository throws `DomainError`)
- Assert that `execute()` calls the repository with the correct params

**Service test rules:**
- No mocks needed — services are pure functions
- Cover all branches: every condition, every edge case
- 100% branch coverage target

**Pattern:** `reference/code-architecture/testing-impl.md` — Grep `## Service Tests`

**Return:** created test file path.
