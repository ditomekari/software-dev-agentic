---
name: builder-test-create-data
description: Write unit tests for mappers and integration tests for repository implementations. Called by builder-test-worker.
user-invocable: false
tools: Read, Write, Glob
---

Write tests for a data layer file (mapper or repository impl).

**Preconditions:**
- Read the target file: extract class, constructor deps, and public methods
- Check `__tests__/mocks/` for existing mocks — create missing ones via `test-create-mock` first
- Output location:
  - Mapper → `__tests__/data/mappers/[Name]Mapper.test.ts`
  - Repository impl → `__tests__/data/repositories/[Feature]RepositoryImpl.test.ts`

**Mapper test rules:**
- No mocks needed
- Test `toEntity()` with a real DTO — assert every field is mapped correctly
- Test nullable/optional fields: pass `null` values, assert they map correctly

**Repository integration test rules:**
- Mock: data source, mapper, error mapper
- For each public method, cover:
  - Happy path: correct params forwarded → DTO mapped → entity returned
  - HTTP 400 → `DomainError.badRequest`
  - HTTP 401 → `DomainError.unauthorized`
  - HTTP 403 → `DomainError.forbidden`
  - HTTP 404 → `DomainError.notFound`
  - HTTP 500 → `DomainError.serverError`
  - Network failure (no response) → `DomainError.networkFailure`
  - Assert `errorMapper.map` is always called with the original error

**Pattern:** `reference/code-architecture/testing-impl.md` — Grep `## Mapper Tests`, `## Repository Tests`

**Return:** created test file path.
