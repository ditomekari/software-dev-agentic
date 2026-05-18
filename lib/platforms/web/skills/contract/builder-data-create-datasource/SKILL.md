---
name: builder-data-create-datasource
description: Create a remote data source interface and Axios implementation. Called by data-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create two files for a remote (external API) data source:
1. `src/data/data-sources/remote/[Feature]RemoteDataSource.ts` — interface
2. `src/data/data-sources/remote/[Feature]RemoteDataSourceImpl.ts` — Axios implementation

**Preconditions:**
- `src/data/dtos/[Name]DTO.ts` must exist — run `data-create-mapper` first if missing
- Check `Glob: src/data/data-sources/remote/*Impl.ts` — read one to match project style
- Verify `src/data/networking/HTTPClient.ts` exists (seed file)

**Rules:**
- Interface methods accept params and return DTOs (never domain entities)
- Implementation uses injected `HTTPClient` — never import Axios directly
- Use `APIResponse<T>` wrapper type for list responses where applicable

**Pattern:** `reference/code-architecture/data-impl.md` — Grep `## Data Sources`

**Return:** both created file paths. Suggest next step: `data-create-repository-impl`.
