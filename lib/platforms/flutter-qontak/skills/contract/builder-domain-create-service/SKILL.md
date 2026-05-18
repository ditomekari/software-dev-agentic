---
name: builder-domain-create-service
description: Create a Domain Service class for pure synchronous business logic in Flutter Qontak. No async, no I/O.
user-invocable: false
---

Create a Domain Service following `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md ## Domain Services section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md` for `## Domain Services`; only **Read** the full file if the section cannot be located
2. **Locate** path: `features/[prefix]_[feature]/lib/src/domain/services/`
3. **Create** `[concept]_[noun].dart` (e.g. `password_strength_checker.dart`)

## Service Pattern

```dart
// features/[prefix]_[feature]/lib/src/domain/services/[concept]_[noun].dart
import '../entities/[concept].dart';

class [Concept][Noun] {
  /// [Brief description of what this service computes or decides]

  bool isEligible([Concept] entity) {
    // pure logic — no async, no I/O
    return entity.status == SomeStatus.active;
  }

  SomeEnum calculate([Concept] entity) {
    // returns structured data — never formatted strings
    if (entity.count < 1) return SomeEnum.low;
    return SomeEnum.normal;
  }
}
```

## Rules

- **No `async`** — services are pure synchronous
- **No I/O** — no network, no storage, no file access
- **No `@lazySingleton`** unless the service has injectable constructor dependencies — most services are stateless and instantiated directly
- Returns structured data (numbers, booleans, enums) — never formatted display strings
- Stateless — no mutable fields
- Only import from domain layer (entities, enums) — never from data or presentation
- Extract to a service only when: logic is > 3 lines complex, reused by ≥ 2 use cases, or needs isolated testing

## Output

Confirm file path and list all public method signatures.
