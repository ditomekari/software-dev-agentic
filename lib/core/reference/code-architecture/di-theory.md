# Dependency Injection

Canonical, platform-agnostic principles for Dependency Injection across CLEAN Architecture layers.
Platform syntax and patterns: `reference/code-architecture/di-impl.md` in each platform directory.

---

## DI Principles <!-- 12 -->

These rules apply regardless of framework (Next.js React Context, Swinject, get_it):

1. **Constructor injection** — dependencies are declared as constructor parameters, never fetched inside a class body
2. **Depend on interfaces, not implementations** — callers reference abstract types; the container resolves the concrete class
3. **No `new` inside business logic** — use cases, StateHolders, and repository implementations never instantiate their own dependencies
4. **Container owns lifecycle** — the DI container decides whether a dependency is a singleton, feature-scoped, or transient; callers never manage this
5. **One container per runtime boundary** — if your platform has multiple runtimes (e.g. server + client), each runtime gets its own container; never share a container across boundaries

---

## Registration Order <!-- 17 -->

Dependencies must be registered before they are resolved. The correct registration order mirrors the dependency graph:

```
Infrastructure (HTTP client, DB driver)
  → DataSources
  → Mappers
  → Repository Implementations
  → Use Cases
  → StateHolders
```

Register leaf nodes (no dependencies) first. Register consumers after their dependencies.

---

## Scope Rules <!-- 12 -->

| Scope | Use for | Lifetime |
|---|---|---|
| Singleton | Shared infrastructure — HTTP client, token store, logger | App lifetime |
| Feature-scoped | StateHolders and use cases for a single feature | Screen/route lifetime |
| Transient | Stateless helpers, mappers, pure services | Per-resolution |

**Never register a StateHolder as a singleton** — it holds mutable UI state that must be reset when the screen is destroyed.

---

## Testing with DI <!-- 5 -->

- Swap real implementations for test doubles at registration time — the caller never changes
- Each test gets its own container instance — never share container state across tests
- Verify that the container resolves the full dependency graph in an integration test — catches missing registrations before runtime
