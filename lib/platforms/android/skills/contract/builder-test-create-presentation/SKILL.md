---
name: builder-test-create-presentation
description: |
  Generate unit tests for an MVP Presenter using inOrder verification, attachView/detachView lifecycle, and ErrorHandler mock.
user-invocable: false
---

Create Presentation layer tests following `.claude/reference/code-architecture/testing-impl.md ## Presenter Tests section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/testing-impl.md` for `## Presenter Tests`; only **Read** the full file if the section cannot be located
2. **Read** the Presenter class and Contract interface to understand all methods
3. **Locate** test path: `feature_[module]/src/test/java/co/talenta/feature_[module]/presentation/[feature]/`
4. **Create** `[Feature]PresenterTest.kt`

## Presenter Test Pattern

```kotlin
@RunWith(MockitoJUnitRunner::class)
class FeaturePresenterTest {

    @get:Rule val fake = JUnitForger()

    @Mock lateinit var mockView: FeatureContract.View
    @Mock lateinit var mockUseCase: GetFeatureItemsUseCase
    @Mock lateinit var mockSchedulerTransformers: SchedulerTransformers
    @Mock lateinit var mockErrorHandler: ErrorHandler

    private lateinit var presenter: FeaturePresenter

    @Before
    fun setUp() {
        fake.reset(1)
        presenter = FeaturePresenter(mockUseCase, mockSchedulerTransformers, mockErrorHandler)
        presenter.attachView(mockView)
    }

    @After
    fun tearDown() {
        reset(mockView, mockUseCase, mockSchedulerTransformers, mockErrorHandler)
    }

    @Test
    fun test_givenViewAttached_whenLoadData_thenShowLoadingThenData() {
        val items = listOf<FeatureEntity>()
        given(mockUseCase.execute(any())).willReturn(Single.just(items))

        presenter.loadFeatureItems(fake.aString())

        val inOrder = inOrder(mockView)
        inOrder.verify(mockView).showLoading()
        inOrder.verify(mockView).hideLoading()
        inOrder.verify(mockView).showFeatureItems(items)
        inOrder.verifyNoMoreInteractions()
    }

    @Test
    fun test_givenError_whenLoadData_thenErrorHandlerInvoked() {
        val error = RuntimeException("Network error")
        given(mockUseCase.execute(any())).willReturn(Single.error(error))

        presenter.loadFeatureItems(fake.aString())

        val inOrder = inOrder(mockView)
        inOrder.verify(mockView).showLoading()
        inOrder.verify(mockView).hideLoading()
        verify(mockErrorHandler).handle(eq(error), any())
    }

    @Test
    fun test_givenViewDetached_whenLoadData_thenNoViewInteraction() {
        presenter.detachView()

        presenter.loadFeatureItems(fake.aString())

        verifyNoMoreInteractions(mockView)
    }
}
```

## Coverage Targets

- Success path: `showLoading` → `hideLoading` → `showData` in order (use `inOrder`)
- Error path: `showLoading` → `hideLoading` → `errorHandler.handle(...)` in order
- Detached-view path: no view interactions after `detachView()`

## Output

Confirm test file path and list all test method names.
