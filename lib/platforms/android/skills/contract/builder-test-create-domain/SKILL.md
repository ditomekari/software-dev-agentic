---
name: builder-test-create-domain
description: |
  Generate unit tests for a UseCase with given/when/then naming and null-scheduler/logger coverage.
user-invocable: false
---

Create Domain layer tests following `.claude/reference/code-architecture/testing-impl.md ## Use Case Tests section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/testing-impl.md` for `## Use Case Tests`; only **Read** the full file if the section cannot be located
2. **Read** the UseCase class and its Params to understand all parameters and repository calls
3. **Locate** test path: `feature_[module]/src/test/java/co/talenta/feature_[module]/domain/usecase/`
4. **Create** `[UseCase]Test.kt`

## Test Pattern

```kotlin
@RunWith(MockitoJUnitRunner::class)
class GetFeatureItemsUseCaseTest {

    @get:Rule val fake = JUnitForger()

    private lateinit var useCase: GetFeatureItemsUseCase

    @Mock lateinit var mockRepository: FeatureRepository
    @Mock lateinit var mockResult: Single<List<FeatureEntity>>
    @Mock lateinit var mockSchedulerTransformers: SchedulerTransformers
    @Mock lateinit var mockLogger: Logger

    @Before
    fun setUp() { fake.reset(1) }

    @After
    fun tearDown() { reset(mockRepository, mockResult, mockSchedulerTransformers, mockLogger) }

    @Test
    fun test_givenValidParams_whenExecute_thenRepositoryCalledWithCorrectParams() {
        // given
        useCase = GetFeatureItemsUseCase(mockRepository, mockSchedulerTransformers, mockLogger)
        val params = with(fake) { GetFeatureItemsUseCase.Params(id = aString()) }
        given(mockRepository.getFeatureItems(params.id)).willReturn(mockResult)

        // when
        useCase.execute(params)

        // then
        then(mockRepository).should().getFeatureItems(params.id)
        then(mockRepository).shouldHaveNoMoreInteractions()
    }

    @Test
    fun test_givenNullSchedulerAndLogger_whenExecute_thenWorksWithoutThem() {
        // given
        useCase = GetFeatureItemsUseCase(mockRepository)
        val params = with(fake) { GetFeatureItemsUseCase.Params(id = aString()) }
        given(mockRepository.getFeatureItems(params.id)).willReturn(mockResult)

        // when
        useCase.execute(params)

        // then
        then(mockRepository).should().getFeatureItems(params.id)
    }
}
```

## Coverage Targets

- Happy path: repository called with correct params
- Null scheduler/logger: use case works when instantiated with only the repository
- One test method per repository method called by the use case

## Output

Confirm test file path and list all test method names.
