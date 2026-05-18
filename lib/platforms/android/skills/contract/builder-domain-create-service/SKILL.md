---
name: builder-domain-create-service
description: |
  Create a Domain Service class that coordinates multiple use cases or repositories for complex domain logic.
user-invocable: false
---

Create a Domain Service following DI rules in `.claude/reference/code-architecture/di-impl.md ## DI Principles section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/di-impl.md` for `## DI Principles`; only **Read** the full file if the section cannot be located
2. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/domain/`
3. **Create** `[Feature]Service.kt`
4. **Add** `@Provides` entry in the feature's DI module

## Domain Service Pattern

```kotlin
@OpenForTesting
class FeatureService @Inject constructor(
    private val featureRepository: FeatureRepository,
    private val otherRepository: OtherRepository
) {

    fun computeFeatureResult(params: Params): Single<FeatureResult> {
        return featureRepository.getFeatureItems(params.page, params.limit)
            .flatMap { items ->
                otherRepository.getRelatedData(items.map { it.id })
                    .map { related -> FeatureResult(items, related) }
            }
    }

    data class Params(val page: Int, val limit: Int)
}
```

Rules:
- Annotate with `@OpenForTesting`
- Use `@Inject constructor` — never instantiate directly
- Only coordinate repositories and domain logic — no UI or data-layer concerns
- Return `Single<T>` for all async operations
- Name: `[Feature]Service`

## Output

Confirm file path, service class name, and all public method signatures.
