# iOS — Testing

> Concepts and invariants: `reference/code-architecture/testing-theory.md`. This file covers Swift syntax and iOS-specific patterns.

## Test Pyramid <!-- 15 -->

```
          ┌───────────┐
          │  UI Tests  │  Minimal — happy path only
          │ (XCUITest) │
         ─┼───────────┼─
         │ Integration │  Repository + DataSource
         │   Tests     │  ViewModel + UseCase
        ─┼─────────────┼─
        │  Unit Tests   │  Services (highest coverage)
        │               │  UseCases, Mappers, ViewModels
        └───────────────┘
```

## What to Test Per Layer <!-- 9 -->

| Layer | What to test | What NOT to test |
|---|---|---|
| Domain (UseCases, Services) | Business rules, edge cases, error conditions | Implementation details of other layers |
| Data (Mappers, RepositoryImpl) | DTO → entity field mapping; error propagation to domain | Network stack, real server responses |
| Presentation (ViewModel) | State transitions per event; use case call count and params; action emissions | UIKit rendering, view layout |
| UI (XCUITest) | Critical happy-path user journeys only | Business logic, mapping logic |

## Service Tests <!-- 31 -->

Highest priority. Pure input → output, no mocks needed.

```swift
final class LeaveBalanceCalculatorTests: XCTestCase {
    private var sut: LeaveBalanceCalculator!

    override func setUp() {
        super.setUp()
        sut = LeaveBalanceCalculator()
    }

    func test_remainingBalance_noPending_returnsCorrectBalance() {
        let entitlement = LeaveEntitlement(
            annualDays: 12, usedDays: 5, pendingRequests: []
        )
        XCTAssertEqual(sut.remainingBalance(for: entitlement), 7)
    }

    func test_remainingBalance_negativeBalance_cappedAtZero() {
        let entitlement = LeaveEntitlement(
            annualDays: 12,
            usedDays: 10,
            pendingRequests: Array(repeating: PendingLeaveRequest(days: 1, status: .pending), count: 5)
        )
        XCTAssertEqual(sut.remainingBalance(for: entitlement), 0)
    }
}
```

## Presenter Tests <!-- 66 -->

```swift
final class CICOLocationViewModelTest: XCTestCase {
    var sut: CICOLocationViewModel!
    var mockNavigator: CICOLocationNavigatorMock!
    var mockPostSubmitCICOUseCase: PostSubmitCICOUseCaseMock!
    var disposeBag: DisposeBag!

    override func setUp() {
        super.setUp()
        mockNavigator = CICOLocationNavigatorMock()
        mockPostSubmitCICOUseCase = PostSubmitCICOUseCaseMock()
        disposeBag = DisposeBag()

        sut = CICOLocationViewModel(
            navigator: mockNavigator,
            displayMode: .fullScreen,
            type: .clockIn,
            scheduleData: nil,
            currentLocation: nil,
            postSubmitCICOUseCase: mockPostSubmitCICOUseCase
        )
    }

    override func tearDown() {
        sut = nil
        mockNavigator = nil
        mockPostSubmitCICOUseCase = nil
        disposeBag = nil
        super.tearDown()
    }

    func test_emitEvent_viewDidLoad_shouldUpdateState() {
        // Arrange
        var receivedStates: [CICOLocationViewModelState] = []

        sut.stateDriver
            .drive(onNext: { state in
                receivedStates.append(state)
            })
            .disposed(by: disposeBag)

        // Act
        sut.emitEvent(.viewDidLoad)

        // Assert
        XCTAssertEqual(receivedStates.last?.appBarTitle, "Check In")
    }

    func test_emitEvent_submitButtonTapped_success_shouldNavigateToSuccess() {
        // Arrange
        let model = RequestLiveAttendanceModel()
        mockPostSubmitCICOUseCase.resultToReturn = .success(model)

        // Act
        sut.emitEvent(.submitButtonTapped)

        // Assert
        XCTAssertEqual(mockPostSubmitCICOUseCase.callCount, 1)
        XCTAssertNotNil(mockPostSubmitCICOUseCase.paramsReceived)
        XCTAssertEqual(mockPostSubmitCICOUseCase.paramsReceived?.companyId, expectedCompanyId)
    }
}
```

## Mock Pattern <!-- 40 -->

```swift
// TalentaTests/Mock/Module/TalentaTM/Domain/UseCase/PostSubmitCICOUseCaseMock.swift
class PostSubmitCICOUseCaseMock: UseCaseProtocol {
    typealias Params = PostSubmitCICOUseCase.Params
    typealias Model = RequestLiveAttendanceModel

    var callCount = 0
    var paramsReceived: Params?
    var resultToReturn: Result<RequestLiveAttendanceModel, BaseErrorModel>?

    func execute(
        params: Params,
        completion: @escaping (Result<RequestLiveAttendanceModel, BaseErrorModel>) -> Void
    ) {
        callCount += 1
        paramsReceived = params

        if let result = resultToReturn {
            completion(result)
        }
    }

    func reset() {
        callCount = 0
        paramsReceived = nil
        resultToReturn = nil
    }
}
```

**Testing Pattern:**
- Arrange-Act-Assert structure
- Mock all dependencies
- Track call counts and parameters
- Reset mocks in `tearDown()`
- Test state changes via `stateDriver`
- Test actions via `actionDriver`

## Mapper Tests <!-- 41 -->

Test that Response DTOs are correctly converted to Domain Models.

```swift
// TalentaTests/Mock/Module/[Feature]/Data/Mapper/[Feature]ModelMapperTests.swift
class EmployeeModelMapperTests: XCTestCase {
    var sut: EmployeeModelMapper!

    override func setUp() {
        super.setUp()
        sut = EmployeeModelMapper()
    }

    func test_fromResponseToModel_mapsAllFields() {
        let response = EmployeeResponse(id: 1, name: "John Doe", isActive: true)

        let model = sut.fromResponseToModel(from: response)

        XCTAssertEqual(model.id, 1)
        XCTAssertEqual(model.name, "John Doe")
        XCTAssertTrue(model.isActive)
    }

    func test_fromResponseToModel_handlesNilFields() {
        let response = EmployeeResponse(id: nil, name: nil, isActive: nil)

        let model = sut.fromResponseToModel(from: response)

        XCTAssertEqual(model.id, 0)    // .orZero()
        XCTAssertEqual(model.name, "") // .orEmpty()
        XCTAssertFalse(model.isActive) // .orFalse()
    }
}
```

**Rules:**
- One test for the happy path (all fields present)
- One test for nil handling — verify `.orZero()`, `.orEmpty()`, `.orFalse()` defaults
- Every Entity field must appear in at least one assertion

## Mock vs Real <!-- 12 -->

| Use a mock/stub when… | Use a real implementation when… |
|---|---|
| The dependency has I/O (network, HTTP, DB) | The dependency is pure (Mapper, Domain Service) |
| The test must control exact return values | The test verifies the full integration path |
| Unit test speed matters | Correctness of full wiring matters — integration test |

**Never mock Mappers or Domain Services** — they are pure functions. Test them with real inputs and outputs (see Mapper Tests above).

**Mock creation:** Use the Mock Pattern above — a concrete class implementing the protocol, with `callCount`, `paramsReceived`, and `resultToReturn` properties.

## Repository Tests <!-- 52 -->

Test that RepositoryImpl correctly bridges DataSource results to Domain completions.

```swift
// TalentaTests/Mock/Module/[Feature]/Data/Repository/[Feature]RepositoryImplTests.swift
class EmployeeRepositoryImplTests: XCTestCase {
    var sut: EmployeeRepositoryImpl!
    var dataSourceMock: EmployeeDataSourceMock!
    var mapperMock: EmployeeModelMapperMock!

    override func setUp() {
        super.setUp()
        dataSourceMock = EmployeeDataSourceMock()
        mapperMock = EmployeeModelMapperMock()
        sut = EmployeeRepositoryImpl(dataSource: dataSourceMock, mapper: mapperMock)
    }

    func test_getEmployee_success_callsCompletion_withMappedModel() {
        let response = EmployeeResponse(id: 1, name: "John")
        let expectedModel = EmployeeModel(id: 1, name: "John")
        dataSourceMock.resultToReturn = .success(response)
        mapperMock.modelToReturn = expectedModel

        var receivedResult: Result<EmployeeModel, BaseErrorModel>?
        sut.getEmployee(params: .init(id: "1")) { receivedResult = $0 }

        XCTAssertEqual(try? receivedResult?.get().id, 1)
        XCTAssertEqual(mapperMock.fromResponseCallCount, 1)
    }

    func test_getEmployee_failure_propagatesError() {
        let error = BaseErrorModel(message: "Not found")
        dataSourceMock.resultToReturn = .failure(error)

        var receivedResult: Result<EmployeeModel, BaseErrorModel>?
        sut.getEmployee(params: .init(id: "99")) { receivedResult = $0 }

        if case .failure(let e) = receivedResult {
            XCTAssertEqual(e.message, "Not found")
        } else {
            XCTFail("Expected failure")
        }
    }
}
```

**Rules:**
- Mock both DataSource and Mapper — test RepositoryImpl in isolation
- One success test, one failure test per method
- Verify mapper is called on success; verify error is passed through unchanged on failure

## Test Naming Convention <!-- 11 -->

Pattern: `test_[unitUnderTest]_[scenario]_[expectedOutcome]`

Examples:

- `test_remainingBalance_noPending_returnsCorrectBalance`
- `test_remainingBalance_negativeBalance_cappedAtZero`
- `test_fromResponseToModel_mapsAllFields`
- `test_getEmployee_success_callsCompletion_withMappedModel`
- `test_emitEvent_viewDidLoad_shouldUpdateState`
