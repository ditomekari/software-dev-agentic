---
name: builder-test-create-data
description: |
  Generate unit tests and mocks for a Mapper or DataSource in the Data layer.
user-invocable: false
---

Create Data layer tests following `.claude/reference/code-architecture/testing-impl.md ## Mapper Tests section` and patterns in `.claude/reference/testing-patterns-advanced.md`.

## Steps

1. **Grep** `.claude/reference/testing-patterns-advanced.md` for the relevant pattern keyword; only **Read** the full file if the section cannot be located
2. **Read** the Mapper/DataSource and corresponding Response/Entity files
3. **Locate** test paths:
   - Tests: `TalentaTests/Module/[Module]/Data/`
   - Mocks: `TalentaTests/Mock/Module/[Module]/Data/`
4. **Create** test file(s)

## Mapper Test Pattern

```swift
final class [Feature]ModelMapperTest: XCTestCase {
    var sut: [Feature]ModelMapper!

    override func setUp() {
        super.setUp()
        sut = [Feature]ModelMapper()
    }

    func test_fromResponseToModel_mapsAllFields() {
        let response = [Feature]Response(
            id: 42,
            name: "Test Name",
            isActive: true
        )

        let model = sut.fromResponseToModel(from: response)

        XCTAssertEqual(model.id, 42)
        XCTAssertEqual(model.name, "Test Name")
        XCTAssertTrue(model.isActive)
    }

    func test_fromResponseToModel_nilFields_usesDefaults() {
        let response = [Feature]Response(id: nil, name: nil, isActive: nil)

        let model = sut.fromResponseToModel(from: response)

        XCTAssertEqual(model.id, 0)       // .orZero() default
        XCTAssertEqual(model.name, "")    // .orEmpty() default
        XCTAssertFalse(model.isActive)    // .orFalse() default
    }
}
```

## DataSource Mock Pattern

```swift
final class [Feature]DataSourceMock: [Feature]DataSourceProtocol {
    var callCount = 0
    var capturedParams: [UseCase].Params?
    var mockResult: [Result<[Feature]Response, BaseErrorModel>] = []

    func methodName(params: [UseCase].Params,
                    completion: @escaping (Result<[Feature]Response, BaseErrorModel>) -> Void) {
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

## Coverage Targets

**Mapper tests:**
- All fields mapped correctly (happy path)
- All nil fields produce correct defaults (`.orEmpty()`, `.orZero()`, `.orFalse()`)
- Nested optional chains produce correct output

**DataSource tests (if testing RepositoryImpl):**
- Success: DataSource result → mapped to Model → completion called with `.success`
- Failure: DataSource error → completion called with `.failure`, error unchanged

## Output

Confirm test file path(s), mock file path(s), and list all test method names.
