# Presentation Layer

Canonical, platform-agnostic definitions for the Presentation layer.
Platform syntax and patterns: `reference/code-architecture/presentation-impl.md` in each platform directory.

---

## Dependency Rule <!-- 13 -->

Presentation depends on Domain only. It never imports from the Data layer.

```
Domain  ←  Presentation
```

Allowed imports: domain use case interfaces, domain entities, language primitives.
Forbidden: any DataSource, RepositoryImpl, DTO, mapper, HTTP client, or database type.

---

## StateHolder <!-- 15 -->

A **StateHolder** is the single source of truth for a screen's UI state. Platform names vary (ViewModel, BLoC, Presenter) but the contract is identical across platforms.

**Invariants:**
- Owns no view imports — no UI framework, no widget, no component type
- Depends on use case interfaces only — never calls repositories or data sources directly
- Use cases are injected via DI — never instantiated directly inside the StateHolder
- Exposes state as a read-only stream or observable — UI observes, never mutates
- One StateHolder per screen — never shared across screens unless explicitly scoped

**When to create:** One StateHolder per screen. Created before the screen that observes it.

---

## State <!-- 20 -->

**State** is an immutable snapshot of what the UI should render at a given moment.

**Invariants:**
- Immutable — produced by the StateHolder, never mutated by the UI
- Covers all render cases: loading, data (success), error
- No view logic — no CSS classes, no display strings, no format calls; formatting happens in the UI layer
- Typed — each field has a declared type; avoid untyped `any` or `Object`

**Common shape:**

```
loading  →  no data yet; UI shows a spinner or skeleton
data     →  domain entities or view-ready primitives ready to render
error    →  domain error type; UI decides how to display it
```

---

## Events / Input <!-- 11 -->

**Events** (also called Input or Intent) represent user intentions flowing into the StateHolder.

**Invariants:**
- Named after user actions, not UI mechanics — `SubmitForm`, not `ButtonClicked`
- Carry only the data needed for the operation — no raw UI event objects
- Processed by the StateHolder — the UI never acts on events directly

---

## Actions / Output <!-- 11 -->

**Actions** (also called Output or SideEffects) represent one-time side effects the StateHolder emits after processing an event.

**Invariants:**
- One-shot — consumed once; not part of persistent state
- Named after the outcome — `NavigateToDetail`, `ShowErrorToast`, `CloseScreen`
- Navigation targets are abstract — the StateHolder says *what*, the UI/navigator decides *how*

---

## StateHolder Contract <!-- 15 -->

The **StateHolder contract** is a written handoff artifact that `builder-feature-worker` produces for `builder-ui-worker`. It is not a code file — it is a structured summary written to `.claude/runs/<feature>/stateholder-contract.md`.

**Required fields:**
- StateHolder class/hook name and file path
- State fields (name, type, purpose)
- Event/Action cases (name, payload if any)
- Navigator/coordinator protocol name and methods (if navigation is involved)
- DI factory method or binding key

**Why it exists:** `builder-ui-worker` must know the StateHolder's public API before writing the screen. The contract file is the handoff boundary — `builder-ui-worker` reads the file path, never the source file.

---

## Creation Order <!-- 10 -->

```
Use Cases (from builder-backend-orchestrator) → StateHolder → StateHolder contract → Screen (builder-ui-worker)
```

Never write the screen before the StateHolder contract exists.

---

## Layer Invariants <!-- 7 -->

- StateHolder never imports from the data layer — no DTOs, no datasources, no mappers
- Use cases injected via DI — never `new UseCase()` inside a StateHolder
- State is read-only from the UI's perspective — UI observes, never mutates
- Actions are one-shot — never stored in persistent state
- Navigation decisions belong to a navigator/coordinator — StateHolder emits the intent, not the destination implementation
