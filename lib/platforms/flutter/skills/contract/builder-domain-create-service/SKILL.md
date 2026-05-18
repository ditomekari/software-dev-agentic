---
name: builder-domain-create-service
description: Create a Domain Service class for pure synchronous business logic.
user-invocable: false
---

Create a Domain Service following `.claude/reference/code-architecture/domain-impl.md ## Domain Services section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Domain Services`; only **Read** the full file if the section cannot be located
2. **Locate** path: `lib/src/features/[feature]/domain/services/`
3. **Create** `[feature]_[noun].dart` (e.g. `leave_balance_calculator.dart`)

## Service Pattern

```dart
import '../entities/[feature]_entity.dart';

class [Feature][Noun] {
  /// [Brief description of what this service computes or decides]

  bool isEligible([Feature]Entity entity) {
    // pure logic — no async, no I/O
  }

  int calculate([Feature]Entity entity) {
    // returns structured data — never formatted strings
  }
}
```

Rules:
- **No `async`** — services are pure synchronous
- **No I/O** — no network, no storage, no file access
- Returns structured data (numbers, booleans, enums) — never formatted display strings
- No `@lazySingleton` unless the service has injectable dependencies
- Stateless — no mutable fields
- Extract to a service only when: logic is > 3 lines complex, reused by ≥ 2 use cases, or needs isolated testing

## Output

Confirm file path and list all public method signatures.
