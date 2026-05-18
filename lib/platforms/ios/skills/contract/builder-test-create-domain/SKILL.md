---
name: builder-test-create-domain
description: |
  Generate unit tests and mocks for a UseCase and/or Repository in the Domain layer.
user-invocable: false
---

Create Domain layer tests following `.claude/reference/code-architecture/testing-impl.md ## Service Tests, ## Mapper Tests sections` and patterns in `.claude/reference/testing-patterns-advanced.md`.

## Steps

1. **Grep** `.claude/reference/testing-patterns-advanced.md` for the relevant pattern keyword; only **Read** the full file if the section cannot be located
2. **Read** the UseCase and Repository protocol files
3. **Locate** test paths:
   - Tests: `TalentaTests/Module/[Module]/Domain/UseCase/`
   - Mocks: `TalentaTests/Mock/Module/[Module]/Domain/UseCase/`
4. **Create** test file and mock(s)

## Mock Pattern

```swift
final class [UseCase]Mock: [UseCase]Protocol {
    var callCount = 0
    var capturedParams: [UseCase].Params?
    var mockResult: [Result<Model, BaseErrorModel>] = []

    func call(params: [UseCase].Params,
              completion: @escaping (Result<Model, BaseErrorModel>) -> Void) {
        callCount += 1
        capturedParams = params
        completion(mockResult[safe: callCount - 1] ?? .failure(.unknown()))
    }

    func reset() {
        callCount = 0
        capturedParams = nil
        mockResult = []
    }
}
```

## Test Pattern

```swift
final class [UseCase]Test: XCTestCase {
    var sut: [UseCase]!
    var repositoryMock: [Feature]RepositoryMock!

    override func setUp() {
        super.setUp()
        repositoryMock = [Feature]RepositoryMock()
        sut = [UseCase](repository: repositoryMock)
    }

    override func tearDown() {
        repositoryMock.reset()
        sut = nil
        super.tearDown()
    }

    func test_call_success_forwardsModelFromRepository() {
        let expected = [Feature]Model.createMock()
        repositoryMock.mockResult = [.success(expected)]

        var result: [Feature]Model?
        sut.call(params: .init(param: "value")) { r in
            if case .success(let m) = r { result = m }
        }

        XCTAssertEqual(repositoryMock.callCount, 1)
        XCTAssertEqual(result?.id, expected.id)
    }

    func test_call_failure_forwardsError() {
        let error = BaseErrorModel.createMock()
        repositoryMock.mockResult = [.failure(error)]

        var receivedError: BaseErrorModel?
        sut.call(params: .init(param: "value")) { r in
            if case .failure(let e) = r { receivedError = e }
        }

        XCTAssertNotNil(receivedError)
    }
}
```

## Coverage Targets

- Success path (happy path)
- Failure path (error forwarding)
- Params correctly passed to repository (check `capturedParams`)

## Output

Confirm test file path, mock file path, and list all test method names.
