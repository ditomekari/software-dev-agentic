# Android — Testing Patterns

## Test Pyramid <!-- 11 -->

| Layer | Type | Tool | Target ratio |
|---|---|---|---|
| Domain (use cases, services) | Unit | JUnit4 + Mockito | Heavy — fast, isolated |
| Data (mappers, repository impl) | Unit | JUnit4 + Mockito | Heavy |
| Presentation (presenters) | Unit | JUnit4 + Mockito + RxJava test schedulers | Medium |
| UI (activity/fragment) | Instrumented | Espresso | Light — slow, avoid |

Run `./gradlew test` for unit tests; `./gradlew connectedAndroidTest` for instrumented.

## What to Test Per Layer <!-- 9 -->

| Layer | What to test | What NOT to test |
|---|---|---|
| Domain (UseCases, Services) | Business rules, edge cases, error conditions | Implementation details of other layers |
| Data (Mappers, RepositoryImpl) | Response → entity field mapping; ApiException → DomainException propagation | Real HTTP responses, network stack |
| Presentation (Presenter) | View method call order; use case invocations; detached-view safety | Activity/Fragment lifecycle internals |
| UI (Espresso) | Critical happy-path journeys only | Business logic, mapping logic |

## Repository Tests <!-- 48 -->

Test that the repository implementation calls the API and maps the response correctly. Mock the API (`TimeOffApi`) and mapper (`TimeOffRequestMapper`).

```kotlin
@RunWith(MockitoJUnitRunner::class)
class TimeOffRepositoryImplTest {

    @Mock lateinit var mockApi: TimeOffApi
    @Mock lateinit var mockMapper: TimeOffRequestMapper

    private lateinit var repository: TimeOffRepositoryImpl

    @Before
    fun setUp() {
        repository = TimeOffRepositoryImpl(mockApi, mockMapper)
    }

    @Test
    fun test_givenApiSuccess_whenGetRequests_thenMapperIsCalledAndEntityReturned() {
        val response = TimeOffRequestListResponse(data = listOf(TimeOffRequestResponse("1", null, null, null, null, null, 3)), meta = null)
        val entity = TimeOffRequest("1", "", "", "", "", "", 3)
        given(mockApi.getTimeOffRequests(1, 20)).willReturn(Single.just(response))
        given(mockMapper.map(response.data!!.first())).willReturn(entity)

        val result = repository.getTimeOffRequests(1, 20).blockingGet()

        assertEquals(listOf(entity), result)
        then(mockMapper).should().map(response.data!!.first())
    }

    @Test
    fun test_givenApiError_whenGetRequests_thenDomainExceptionPropagated() {
        given(mockApi.getTimeOffRequests(1, 20)).willReturn(Single.error(ApiException(401, "Unauthorized")))

        val error = assertThrows(DomainException.Unauthorized::class.java) {
            repository.getTimeOffRequests(1, 20).blockingGet()
        }
        assertNotNull(error)
    }
}
```

Rules:
- Mock `Api` and `Mapper` — never the repository itself
- Test success path, error path (ApiException → DomainException), and empty list
- Use `.blockingGet()` for synchronous assertion in unit tests

## Unit Test Setup <!-- 30 -->

Test naming convention: `test_given[Condition]_when[Action]_then[ExpectedResult]`

```kotlin
@RunWith(MockitoJUnitRunner::class)
class GetTimeOffRequestsUseCaseTest {

    @get:Rule
    val fake = JUnitForger()

    private lateinit var useCase: GetTimeOffRequestsUseCase

    @Mock lateinit var mockRepository: TimeOffRepository
    @Mock lateinit var mockResult: Single<List<TimeOffRequest>>
    @Mock lateinit var mockSchedulerTransformers: SchedulerTransformers
    @Mock lateinit var mockLogger: Logger

    @Before
    fun setUp() {
        fake.reset(1)
    }

    @After
    fun tearDown() {
        reset(mockRepository, mockResult, mockSchedulerTransformers, mockLogger)
    }
}
```

## Use Case Tests <!-- 35 -->

```kotlin
@Test
fun test_givenValidParams_whenExecute_thenRepositoryShouldGetRequests() {
    // given
    useCase = GetTimeOffRequestsUseCase(mockRepository, mockSchedulerTransformers, mockLogger)
    val params = with(fake) {
        GetTimeOffRequestsUseCase.Params(id = aString())
    }
    given(mockRepository.getTimeOffRequests(params.id)).willReturn(mockResult)

    // when
    useCase.execute(params)

    // then
    then(mockRepository).should().getTimeOffRequests(params.id)
    then(mockRepository).shouldHaveNoMoreInteractions()
}

@Test
fun test_givenNullSchedulerAndLogger_whenExecute_thenWorksWithoutThem() {
    // given
    useCase = GetTimeOffRequestsUseCase(mockRepository)
    val params = with(fake) { GetTimeOffRequestsUseCase.Params(id = aString()) }
    given(mockRepository.getTimeOffRequests(params.id)).willReturn(mockResult)

    // when
    useCase.execute(params)

    // then
    then(mockRepository).should().getTimeOffRequests(params.id)
}
```

## Mapper Tests <!-- 42 -->

```kotlin
@RunWith(MockitoJUnitRunner::class)
class TimeOffRequestMapperTest {

    private lateinit var mapper: TimeOffRequestMapper

    @Before
    fun setUp() { mapper = TimeOffRequestMapper() }

    @Test
    fun test_givenValidResponse_whenMap_thenEntityIsCorrect() {
        val response = TimeOffRequestResponse(
            id = "123", employeeId = "emp-1", startDate = "2024-01-01",
            endDate = "2024-01-05", reason = "Vacation", status = "pending", totalDays = 5
        )
        val result = mapper.map(response)
        assertEquals("123", result.id)
        assertEquals(5, result.totalDays)
    }

    @Test
    fun test_givenNullFields_whenMap_thenDefaultsApplied() {
        val result = mapper.map(TimeOffRequestResponse(null, null, null, null, null, null, null))
        assertEquals("", result.id)
        assertEquals(0, result.totalDays)
    }

    @Test
    fun test_givenListResponse_whenMapList_thenAllEntitiesMapped() {
        val responses = listOf(
            TimeOffRequestResponse("1", null, null, null, null, null, 3),
            TimeOffRequestResponse("2", null, null, null, null, null, 5)
        )
        val results = responses.map { mapper.map(it) }
        assertEquals(2, results.size)
        assertEquals("1", results[0].id)
    }
}
```

## Mock vs Real <!-- 12 -->

| Use a mock/stub when… | Use a real implementation when… |
|---|---|
| The dependency has I/O (Retrofit API, DB) | The dependency is pure (Mapper, domain service) |
| The test must control exact return values | The test verifies full integration wiring |
| Unit test speed matters | Correctness of data transformation matters |

**Never mock Mappers** — they are pure functions. Instantiate directly and test with real input/output.

Use `@Mock` with `MockitoJUnitRunner` for all collaborators (Api, Mapper, Repository, SchedulerTransformers). Use `.blockingGet()` for synchronous assertion on RxJava Singles.

## Presenter Tests <!-- 83 -->

```kotlin
@RunWith(MockitoJUnitRunner::class)
class TimeOffRequestPresenterTest {

    @get:Rule
    val fake = JUnitForger()

    @Mock lateinit var mockView: TimeOffRequestContract.View
    @Mock lateinit var mockUseCase: GetTimeOffRequestsUseCase
    @Mock lateinit var mockSchedulerTransformers: SchedulerTransformers
    @Mock lateinit var mockErrorHandler: ErrorHandler

    private lateinit var presenter: TimeOffRequestPresenter

    @Before
    fun setUp() {
        fake.reset(1)
        presenter = TimeOffRequestPresenter(mockUseCase, mockSchedulerTransformers, mockErrorHandler)
        presenter.attachView(mockView)
    }

    @After
    fun tearDown() {
        reset(mockView, mockUseCase, mockSchedulerTransformers, mockErrorHandler)
    }

    @Test
    fun test_givenViewAttached_whenLoadData_thenShowLoadingThenData() {
        // given
        val featureId = fake.aString()
        val mockData = with(fake) { TimeOffRequest(aString(), aString(), aString(), aString(), aString(), aString(), aPositiveInt()) }
        given(mockUseCase.execute(any())).willReturn(Single.just(listOf(mockData)))

        // when
        presenter.loadTimeOffRequests(featureId)

        // then
        val inOrder = inOrder(mockView)
        inOrder.verify(mockView).showLoading()
        inOrder.verify(mockView).hideLoading()
        inOrder.verify(mockView).showTimeOffRequests(listOf(mockData))
        inOrder.verifyNoMoreInteractions()
    }

    @Test
    fun test_givenError_whenLoadData_thenShowError() {
        // given
        val error = RuntimeException("Network error")
        given(mockUseCase.execute(any())).willReturn(Single.error(error))

        // when
        presenter.loadTimeOffRequests(fake.aString())

        // then
        val inOrder = inOrder(mockView)
        inOrder.verify(mockView).showLoading()
        inOrder.verify(mockView).hideLoading()
        verify(mockErrorHandler).handle(eq(error), any())
    }

    @Test
    fun test_givenViewDetached_whenLoadData_thenNoViewInteraction() {
        // given
        presenter.detachView()

        // when
        presenter.loadTimeOffRequests(fake.aString())

        // then
        verifyNoMoreInteractions(mockView)
    }
}
```

Rules:
- Test naming: `test_given[Condition]_when[Action]_then[ExpectedResult]`
- Use `inOrder(mockView)` to verify call order (showLoading → hideLoading → showData)
- `presenter.attachView(mockView)` in `@Before`, `reset(...)` all mocks in `@After`
- `presenter.detachView()` (not `detach()`) — test that detached presenter ignores use case results
- Always test: success path, error path, detached-view path

## Test Naming Convention <!-- 12 -->

Pattern: `test_given[Condition]_when[Action]_then[ExpectedResult]`

Examples:

- `test_givenApiSuccess_whenGetRequests_thenMapperIsCalledAndEntityReturned`
- `test_givenApiError_whenGetRequests_thenDomainExceptionPropagated`
- `test_givenValidResponse_whenMap_thenEntityIsCorrect`
- `test_givenNullFields_whenMap_thenDefaultsApplied`
- `test_givenViewAttached_whenLoadData_thenShowLoadingThenData`
- `test_givenViewDetached_whenLoadData_thenNoViewInteraction`
