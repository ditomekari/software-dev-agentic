---
name: builder-domain-create-repository
description: |
  Create a Repository interface in the Domain layer for a new feature.
user-invocable: false
---

Create a Repository interface following `.claude/reference/code-architecture/domain-impl.md ## Repository Interfaces section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Repository Interfaces`; only **Read** the full file if the section cannot be located
2. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/domain/repository/`
3. **Create** `[Module]Repository.kt`

## Repository Interface Pattern

```kotlin
interface FeatureRepository {
    fun getFeatureItems(page: Int, limit: Int): Single<List<FeatureEntity>>
    fun submitFeatureAction(params: ActionParams): Single<FeatureEntity>
}
```

Rules:
- Interface only — no implementation in domain layer
- Return `Single<T>` (RxJava 3) for all async operations
- Parameters are domain types — never response/DTO types
- Name: `[Module]Repository`

## Output

Confirm the file path created and list all declared method signatures.
