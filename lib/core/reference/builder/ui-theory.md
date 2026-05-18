# UI Layer

Canonical, platform-agnostic definitions for the UI layer.
Platform syntax and patterns: `reference/builder/presentation-impl.md` in each platform directory (UI artifacts live in the presentation contract file on most platforms).

---

## Dependency Rule <!-- 13 -->

UI depends on Presentation only. It never imports from Domain or Data directly.

```
Presentation  ←  UI
```

Allowed imports: StateHolder contract types, State/Event/Action types, platform UI framework primitives.
Forbidden: use case interfaces, repository interfaces, DTOs, mappers, datasources, or any domain/data type instantiated directly.

---

## Screen <!-- 15 -->

A **Screen** is a full-page view bound to a single StateHolder. It observes state and sends events — it contains no business logic.

**Invariants:**
- Bound to exactly one StateHolder — instantiated via DI, never with direct `new` / `init`
- Observes every State field declared in the StateHolder contract — no State field goes unhandled
- Sends events to the StateHolder for every user interaction — never mutates state directly
- Contains no business logic — conditionals exist only to decide what to render, not what to compute
- No use case calls — all data flows through the StateHolder

**When to create:** One screen per route/destination. Created after the StateHolder contract exists.

---

## Component / Sub-view <!-- 14 -->

A **Component** (also called Sub-view, Widget, or View) is a reusable UI element smaller than a full screen.

**Invariants:**
- Stateless by default — receives data via props/parameters and emits callbacks
- If stateful, bound to a scoped StateHolder — never manages business state inline
- No use case calls — all data passed in from the parent screen or a scoped StateHolder
- Reuse check required before creating — search shared component directories first

**When to create:** When a UI element appears in ≥2 screens, or when a screen section is complex enough to isolate for readability.

---

## Navigator / Coordinator <!-- 14 -->

A **Navigator** (web/Flutter) or **Coordinator** (iOS) owns all navigation logic for a feature or flow.

**Invariants:**
- The Screen delegates navigation intent to the Navigator — it never hard-codes a destination
- The StateHolder emits a navigation Action — the Navigator/Coordinator decides the implementation
- Knows route constants or destination types — the Screen does not
- One coordinator/navigator per feature flow — not per screen

**When to create:** When a screen navigates to another screen. Created after the screen that triggers navigation.

---

## DI Wiring <!-- 13 -->

**DI wiring** registers the StateHolder and its dependencies in the project's DI container for a given screen.

**Invariants:**
- StateHolder registered with the correct scope (feature-scoped, not singleton unless explicitly shared)
- Use cases injected into the StateHolder — never instantiated inside the StateHolder
- DI factory or binding key matches the StateHolder contract exactly

**When to create:** After the Screen and StateHolder exist. Required before the feature is navigable.

---

## Creation Order <!-- 10 -->

```
Screen → Navigator/Coordinator (if navigation needed) → DI wiring
```

The StateHolder and its contract must exist before any UI layer file is written.

---

## Layer Invariants <!-- 7 -->

- UI never mutates state directly — observes only
- UI never calls use cases directly — all interactions go through the StateHolder
- StateHolder instantiated via DI — never `new ViewModel()` / `MyViewModel()` inline
- Navigation delegated to navigator/coordinator — UI emits intent, not destination
- No data layer knowledge — no DTOs, no datasources, no HTTP types visible in UI files
