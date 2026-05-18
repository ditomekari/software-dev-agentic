---
name: builder-pres-create-component
description: Create a reusable UI sub-component (organism or molecule) within a feature — accepts entity props, no DI, no business logic. Called by builder-ui-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create a reusable UI component following `reference/code-architecture/presentation-impl.md`.

## Component Placement

- **Organism** (feature-specific, accepts entities as props) → `src/presentation/features/[feature]/components/[Name].tsx`
- **Molecule/Atom** (reusable across features, primitive props only) → `src/presentation/common/[Name].tsx`

## Steps

1. **Glob** `src/presentation/features/[feature]/components/` or `src/presentation/common/` — read one existing component to match style
2. **Create** the component file

## Component Pattern

```tsx
interface [Name]Props {
  // primitive props or domain entities — no use cases, no DI
  item: FeatureEntity
  onAction?: (id: string) => void
}

export function [Name]({ item, onAction }: [Name]Props) {
  return (
    // render — no hooks that call use cases
  )
}
```

## Rules

- Props are plain values or domain entities — never use cases or repositories
- No `useDI()` call — organisms receive data as props from the parent View
- `'use client'` only if the component uses React state/effects/event handlers
- No business logic — render only

**Pattern:** `reference/code-architecture/presentation-impl.md` — `Grep` for component/organism section.

## Output

Confirm file path and list all props.
