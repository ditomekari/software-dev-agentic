# Data Layer

Canonical, platform-agnostic definitions for the Data layer.
Platform syntax and patterns: `reference/code-architecture/data-impl.md` in each platform directory.

---

## Dependency Rule <!-- 13 -->

Data depends on Domain only. It never imports from Presentation or UI.

```
Domain  ←  Data
```

Allowed imports: domain entities, repository interfaces, language primitives.
Forbidden: any presentation type, UI framework, StateHolder, or view import.

---

## DTOs <!-- 15 -->

A **DTO (Data Transfer Object)** mirrors the raw API or database shape exactly.

**Invariants:**
- No domain logic — plain data container only
- No computed fields — no derived values, no formatting
- No domain entity types — DTOs use primitive types and nested DTOs
- Serialization annotations live here, not on domain entities (`@JsonKey`, `Codable`, `fromJson`)
- Field names match the API/DB schema — not the business domain vocabulary

**When to create:** One DTO per API response type or DB table row. Created before the mapper that consumes it.

---

## Mappers <!-- 15 -->

A **Mapper** converts between a DTO and a domain entity — always defined as an interface with a concrete implementation.

**Invariants:**
- Always interface + implementation — never a plain utility function or static helper
- One direction per method: `toDomain(dto)` converts inward; `toDTO(entity)` converts outward (if write operations exist)
- No I/O — pure transformation only; no network calls, no DB reads
- No business logic — field mapping only; validation belongs in domain use cases
- Null/missing fields handled defensively — never let a missing API field crash the mapper

**When to create:** One mapper per DTO ↔ entity pair. Created after the DTO, before the DataSource implementation.

---

## Data Sources <!-- 14 -->

A **DataSource** is an abstract interface for raw data access — remote (HTTP) or local (DB, cache).

**Invariants:**
- Interface only in the data layer — implementation is injected, never instantiated directly
- Methods return raw data (DTOs or primitives) — never domain entities
- One DataSource per data origin (remote API, local DB, cache) — do not mix sources in one interface
- Throws or returns transport-layer errors — the repository implementation maps these to domain errors

**When to create:** One DataSource interface per data origin per feature. Created after the DTO and mapper, before the repository implementation.

---

## Repository Implementation <!-- 15 -->

A **Repository Implementation** implements the domain repository interface using a DataSource and Mapper.

**Invariants:**
- Implements a domain repository interface — it is the bridge between Data and Domain
- Calls the DataSource for raw data, calls the Mapper to convert to domain entities
- Wraps all DataSource calls with error handling — maps transport errors to domain errors before returning
- Never lets raw HTTP errors, DB exceptions, or transport-layer types propagate to the domain
- Never calls another repository implementation directly

**When to create:** Last in the creation order — after DataSource interface and implementation exist.

---

## Creation Order <!-- 18 -->

**Remote API feature:**

```
DTO → Mapper → DataSource interface → DataSource impl → Repository impl
```

**Local DB feature:**

```
DB Record → DB DataSource interface → DB DataSource impl → DB Mapper → Repository impl
```

Never create a repository implementation before the DataSource it depends on.

---

## Layer Invariants <!-- 5 -->

- Imports from domain layer only — never from presentation or UI
- Raw transport errors never propagate upward — repository implementation maps them to domain errors
- DTOs and DB records never cross into the domain layer — mappers are the boundary
