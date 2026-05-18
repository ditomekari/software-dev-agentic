---
name: builder-domain-create-usecase
description: |
  Create a UseCase extending SingleUseCase with a nested Params class and Dagger wire-up.
user-invocable: false
---

Create a UseCase following `.claude/reference/code-architecture/domain-impl.md ## Use Cases section` and DI rules in `.claude/reference/code-architecture/di-impl.md ## DI Principles section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Use Cases` and `.claude/reference/code-architecture/di-impl.md` for `## DI Principles`; only **Read** a file in full if the section cannot be located
2. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/domain/usecase/`
3. **Create** `[Action][Entity]UseCase.kt`
4. **Add** `@Provides` entry in the feature's DI module

## UseCase Pattern

```kotlin
@OpenForTesting
class GetFeatureItemsUseCase @Inject constructor(
    private val featureRepository: FeatureRepository,
    schedulerTransformer: SchedulerTransformers? = null,
    logger: Logger? = null
) : SingleUseCase<List<FeatureEntity>, GetFeatureItemsUseCase.Params>(
    schedulerTransformer?.applySingleIoSchedulers(),
    logger
) {

    override fun build(params: Params?): Single<List<FeatureEntity>> = params!!.run {
        featureRepository.getFeatureItems(page, limit)
    }

    data class Params(
        val page: Int,
        val limit: Int
    )
}
```

Rules:
- Annotate with `@OpenForTesting` to allow mocking in tests
- Use `@Inject constructor` — never instantiate directly
- Inject `SchedulerTransformers` and `Logger` with nullable defaults
- `Params` is a nested data class inside the use case class
- Name: `[Action][Entity]UseCase`

## Output

Confirm file path, use case class name, Params fields, and DI provider method.
