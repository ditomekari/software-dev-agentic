---
name: pres-wire-di
description: Wire a use case and its dependencies into the DI containers. Called by presentation-worker after data layer artifacts are created.
user-invocable: false
tools: Read, Edit
---

Wire a new use case and its dependencies into the DI containers.

**Preconditions:**
- `src/di/container.server.ts` must exist
- `src/di/container.client.ts` must exist
- All dependency classes (DataSource, Mapper, Repository, UseCase) must exist

**Workflow:**
1. Read `src/di/container.server.ts` — understand current wiring pattern
2. Read `src/di/container.client.ts` — understand current wiring pattern
3. Determine: server-side only, client-side only, or both?
   - Server Actions and RSC reads → `container.server.ts`
   - TanStack Query / client interactions → `container.client.ts`
4. Add the imports and wiring lines in the same style as existing entries

**Rules:**
- Server container: module-level singletons exported as factory functions `() => new Impl(...)`
- Client container: `createClientContainer()` return object using lazy getter pattern
- Add `import 'server-only'` guard check in server container (it must already be there)
- Never add React imports or `client-only` to server container

**Pattern:** `reference/code-architecture/di-impl.md` — Grep `## Server Container`, `## Client Container`

**Return:** which container(s) were updated and what was added.
