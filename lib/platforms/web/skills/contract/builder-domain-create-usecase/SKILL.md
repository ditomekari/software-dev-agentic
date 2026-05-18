---
name: builder-domain-create-usecase
description: Create a use case interface and implementation. Called by domain-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create a use case at `src/domain/use-cases/[feature]/[Verb][Feature]UseCase.ts`.

**Preconditions:**
- File must NOT exist — fail fast if it does
- `src/domain/repositories/[Feature]Repository.ts` must exist — run `domain-create-repository` first if missing

**Rules:**
- One file per operation (GetList, GetById, Create, Update, Delete)
- Interface + `Impl` class in the same file
- `Impl` calls only the repository — no direct data source access
- Zero framework imports in domain layer

**Params pattern by operation:**
- GET single: `{ id: string }`
- GET list: `{ page: number; limit: number; filters?: ... }`
- POST: `{ payload: { [fields] } }`
- PUT: `{ id: string; payload: { [fields] } }`
- DELETE: `{ id: string }`

**Pattern:** `reference/code-architecture/domain-impl.md` — Grep `## Use Cases`

**Return:** created file path. Suggest next step: `data-worker`.
