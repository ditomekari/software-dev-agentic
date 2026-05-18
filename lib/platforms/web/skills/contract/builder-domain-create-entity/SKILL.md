---
name: builder-domain-create-entity
description: Create a domain entity interface. Called by domain-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create a domain entity at `src/domain/entities/[Name].ts`.

**Preconditions:**
- File must NOT exist — fail fast if it does
- `Glob: src/domain/entities/*.ts` — read one existing entity to match project style

**Rules:**
- Every property is `readonly`
- Zero imports (no framework, no data layer, no presentation)
- Interface only — no class, no decorators
- Properties represent business concepts, not API field names

**Pattern:** `reference/code-architecture/domain-impl.md` — Grep `## Entities`

**Return:** created file path. Suggest next step: `domain-create-repository` or `domain-create-usecase`.
