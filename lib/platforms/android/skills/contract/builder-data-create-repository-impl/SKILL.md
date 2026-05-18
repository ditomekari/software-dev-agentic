---
name: builder-data-create-repository-impl
description: |
  Create a Repository implementation in the Data layer, injecting API and Mapper via Dagger.
user-invocable: false
---

Create a Repository implementation following `.claude/reference/code-architecture/data-impl.md ## Repository Implementations section` and DI rules in `.claude/reference/code-architecture/di-impl.md`.

## Steps

1. **Grep** `.claude/reference/code-architecture/data-impl.md` for `## Repository Implementations` and `.claude/reference/code-architecture/di-impl.md` for `## DI Module`; only **Read** a file in full if the section cannot be located
2. **Read** the domain Repository interface and Mapper to understand method signatures
3. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/data/repoimpl/`
4. **Create** `[Module]RepositoryImpl.kt`
5. **Add** `@Provides` binding in the DI module

## Repository Impl Pattern

```kotlin
class FeatureRepositoryImpl @Inject constructor(
    private val api: FeatureApi,
    private val mapper: FeatureEntityMapper
) : FeatureRepository {

    override fun getFeatureItems(page: Int, limit: Int): Single<List<FeatureEntity>> {
        return api.getFeatureItems(page, limit)
            .map { response ->
                response.data?.map { mapper.map(it) } ?: emptyList()
            }
    }
}
```

## DI Binding

```kotlin
@Provides
fun provideFeatureRepository(
    api: FeatureApi,
    mapper: FeatureEntityMapper
): FeatureRepository {
    return FeatureRepositoryImpl(api, mapper)
}
```

Rules:
- `@Inject constructor` on the impl class — Dagger resolves constructor params automatically
- The `@Provides` method binds the interface to the impl; Dagger calls the `@Inject constructor` internally
- Map response to domain entity via mapper before returning
- Implement every method declared in the domain repository interface
- Never expose response types outside the data layer

## Output

Confirm file path, list all implemented methods, and confirm DI binding added.
