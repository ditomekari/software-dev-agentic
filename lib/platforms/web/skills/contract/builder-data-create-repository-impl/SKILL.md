---
name: builder-data-create-repository-impl
description: Create a remote repository implementation that adapts a data source to a domain repository interface. Called by data-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create `src/data/repositories/[Feature]RepositoryImpl.ts`.

**Preconditions:**
- `src/domain/repositories/[Feature]Repository.ts` must exist
- `src/data/data-sources/remote/[Feature]RemoteDataSource.ts` must exist
- `src/data/mappers/[Name]Mapper.ts` must exist
- `src/data/mappers/ErrorMapper.ts` must exist (seed file)

**Rules:**
- Implements the domain repository interface — never introduces new methods
- Every method wraps with `try/catch → this.errorMapper.map(error)` — no exceptions
- Calls mapper to convert DTOs to entities — never returns raw DTOs
- Constructor injects: `dataSource`, `mapper`, `errorMapper`

**Pattern:** `reference/code-architecture/data-impl.md` — Grep `## Repository Implementation`

**Return:** created file path. Suggest next step: `pres-wire-di`.
