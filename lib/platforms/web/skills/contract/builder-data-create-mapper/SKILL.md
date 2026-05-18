---
name: builder-data-create-mapper
description: Create a DTO and its mapper (interface + Impl). Called by data-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create two files for a new entity's data representation:
1. `src/data/dtos/[Name]DTO.ts`
2. `src/data/mappers/[Name]Mapper.ts`

**Preconditions:**
- `src/domain/entities/[Name].ts` must exist — run `domain-create-entity` first if missing
- Check `Glob: src/data/mappers/*.ts` — read one existing mapper to match project style

**DTO rules:**
- Mirrors raw API response shape (snake_case if the API returns it)
- All fields non-readonly
- No domain logic

**Mapper rules:**
- Interface: `[Name]Mapper` with `toEntity(dto: [Name]DTO): [Name]`
- Implementation: `[Name]MapperImpl implements [Name]Mapper`
- Handle null/undefined optional fields explicitly (`.orEmpty()`, `.orZero()`, etc.)
- Map API field names to domain property names

**Pattern:** `reference/code-architecture/data-impl.md` — Grep `## DTOs`, `## Mappers`

**Return:** both created file paths. Suggest next step: `data-create-datasource`.
