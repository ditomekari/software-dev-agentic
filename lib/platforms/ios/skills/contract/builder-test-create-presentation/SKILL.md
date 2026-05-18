---
name: builder-test-create-presentation
description: |
  Generate a complete StateHolder *(iOS: ViewModel)* test file with mocks covering all events and branches.
user-invocable: false
---

Create a ViewModel test suite following `.claude/reference/code-architecture/testing-impl.md ## Presenter Tests, ## Mapper Tests sections` and patterns in `.claude/reference/testing-patterns-advanced.md`.

## Steps

1. **Grep** `.claude/reference/testing-patterns-advanced.md` for the relevant pattern keyword; only **Read** the full file if the section cannot be located
2. **Read** the ViewModel file completely — map all Events, State fields, Actions
3. **Read** existing mock files (UseCase, Repository, Navigator) if they exist
4. **Locate** paths:
   - Test: `TalentaTests/Module/[Module]/Presentation/ViewModel/[Name]ViewModelTest.swift`
   - Mocks: `TalentaTests/Mock/Module/[Module]/Domain/UseCase/`
5. **Create** test file and any missing mocks
6. **Optionally run ViewModelTestGen** for complex ViewModels: `scripts/viewmodel-testgen.sh [ViewModelName]`

## Test File Structure

```swift
final class [Feature]ViewModelTest: XCTestCase {
    // MARK: - Test Infrastructure
    var viewModel: [Feature]ViewModel!
    var useCaseMock: [UseCase]Mock!
    var navigatorMock: [Feature]NavigatorMock!
    var disposeBag: DisposeBag!
    var testScheduler: TestScheduler!

    override func setUp() {
        super.setUp()
        useCaseMock = [UseCase]Mock()
        navigatorMock = [Feature]NavigatorMock()
        disposeBag = DisposeBag()
        testScheduler = TestScheduler(initialClock: 0)
    }

    override func tearDown() {
        viewModel = nil
        useCaseMock.reset()
        navigatorMock.reset()
        disposeBag = nil
        super.tearDown()
    }

    @discardableResult
    func createViewModel(/* branch-directing params */) -> [Feature]ViewModel {
        viewModel = [Feature]ViewModel(
            useCase: useCaseMock,
            navigator: navigatorMock
        )
        return viewModel
    }

    // MARK: - [EventName] Tests
    func test[EventName]Event_[Logic]_[Condition]_[Outcome]() {
        // GIVEN
        useCaseMock.mockResult = [.success([Feature]Model.createMock())]
        createViewModel()
        var capturedStates: [State] = []
        viewModel.stateDriver
            .drive(onNext: { capturedStates.append($0) })
            .disposed(by: disposeBag)

        // WHEN
        viewModel.emitEvent(.[eventName])
        testScheduler.start()

        // THEN
        XCTAssertEqual(useCaseMock.callCount, 1)
        XCTAssertNotNil(capturedStates.last?.dataState.data)
    }
}
```

## Coverage Requirements

For each Event in the ViewModel:
- At least one success path test
- At least one failure/error path test
- One test per guard failure (noop paths)
- One test per enum branch in switch statements

Follow **5-Point Test Creation Process** from `testing-patterns.md` for each test case.

## Mock Requirements

Each mock must have:
- `callCount` tracking
- `capturedParams` storage
- Sequential `mockResult: [Result<...>]` array
- `reset()` method

Navigator mock returns `Observable` or `Driver` — default to `.empty()`.

## Output

Confirm test file path, mock file paths, list all test method names grouped by Event, and flag any TODO items that need runtime data to complete.
