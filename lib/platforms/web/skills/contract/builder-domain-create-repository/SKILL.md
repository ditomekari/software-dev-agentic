---
name: builder-domain-create-repository
description: Create a domain repository interface. Called by domain-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create a repository interface at `src/domain/repositories/[Feature]Repository.ts`.

**Preconditions:**
- File must NOT exist — fail fast if it does
- `src/domain/entities/[Name].ts` must exist — run `domain-create-entity` first if missing

**Rules:**
- Interface only — no implementation
- Methods return domain entities, never DTOs or DB records
- Method signatures match the CRUD operations requested

**Pattern:** `reference/code-architecture/domain-impl.md` — Grep `## Repository Interfaces`

**Return:** created file path. Suggest next step: `domain-create-usecase`.
