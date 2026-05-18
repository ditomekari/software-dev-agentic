---
name: builder-domain-create-service
description: Create a pure domain service for business logic that spans multiple entities or use cases. Called by domain-worker.
user-invocable: false
---

Create a domain service at `Talenta/Domain/Services/[Name]Service.swift`.

**Preconditions:**
- File must NOT exist — fail fast if it does
- Verify the service is genuinely pure logic — if it requires I/O or async, it belongs in a use case instead

**Rules:**
- Synchronous pure functions only — no async, no network calls, no side effects
- Zero imports from `Foundation` networking APIs, UIKit, or data layer modules
- No display formatting (no `formatCurrency`, no color names) — return structured data (numbers, enums, booleans)
- Defined as a `struct` with static methods, or a `final class` — match existing project style

**Pattern:** **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Services`; only **Read** the full file if the section cannot be located

**Return:** created file path.
