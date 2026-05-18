---
name: builder-domain-create-service
description: Create a pure domain service for business logic that spans multiple entities or use cases. Called by domain-worker.
user-invocable: false
tools: Read, Write, Glob
---

Create a domain service at `src/domain/services/[Name]Service.ts`.

**Preconditions:**
- File must NOT exist — fail fast if it does
- Verify the service is genuinely pure logic — if it requires I/O or async, it belongs in a use case instead

**Rules:**
- Synchronous pure functions only — no `async`, no `fetch`, no DOM APIs, no side effects
- Zero imports from `react`, `next`, `axios`, `src/data/`, or `src/presentation/`
- No display formatting (no `formatCurrency`, no CSS class names) — return structured data (numbers, enums, booleans)
- Exported as a class with static methods, or plain exported functions — your call, match existing project style

**Pattern:** `reference/code-architecture/domain-impl.md` — Grep `## Services`

**Return:** created file path.
