# iOS — Domain Layer

> Concepts and invariants: `reference/code-architecture/domain-theory.md`. This file covers Swift syntax and iOS-specific patterns.

## Dependency Rule <!-- 14 -->

Domain is the innermost layer — it imports nothing from outer layers.

**Allowed:** Swift standard library, `Foundation` primitives (`Date`, `UUID`, `Decimal`, `String`, `Int`, `Bool`).

**Forbidden:**
- `import UIKit` — any UIKit type signals a presentation leak into domain
- `import RxSwift` / `import Combine` — reactive frameworks belong in data or presentation
- `import Alamofire` / `import Moya` — networking belongs in data
- Any type defined in a `*RepositoryImpl`, `*DataSource`, or `*Response` file

---

## Entities <!-- 70 -->

```swift
// Domain/Entities/CICO/RequestLiveAttendanceModel.swift
struct RequestLiveAttendanceModel {
    let actualBreakStart: String
    let isBreakStart: Bool
    let isBreakEnd: Bool
    let currentShiftDate: String
    let currentShiftName: String
    let actualCheckIn: String
    let actualCheckOut: String
    let faceRecogAccuracy: Double
    let serverTime: String
    let processedAsync: Bool
    let ipAddressStatus: Bool

    init(
        actualBreakStart: String = "",
        isBreakStart: Bool = false,
        isBreakEnd: Bool = false,
        currentShiftDate: String = "",
        currentShiftName: String = "",
        actualCheckIn: String = "",
        actualCheckOut: String = "",
        faceRecogAccuracy: Double = 0.0,
        serverTime: String = "",
        processedAsync: Bool = false,
        ipAddressStatus: Bool = false
    ) {
        self.actualBreakStart = actualBreakStart
        self.isBreakStart = isBreakStart
        self.isBreakEnd = isBreakEnd
        self.currentShiftDate = currentShiftDate
        self.currentShiftName = currentShiftName
        self.actualCheckIn = actualCheckIn
        self.actualCheckOut = actualCheckOut
        self.faceRecogAccuracy = faceRecogAccuracy
        self.serverTime = serverTime
        self.processedAsync = processedAsync
        self.ipAddressStatus = ipAddressStatus
    }
}

// copyWith for immutable updates
extension RequestLiveAttendanceModel {
    func copyWith(
        actualBreakStart: String? = nil,
        isBreakStart: Bool? = nil,
        serverTime: String? = nil
        // ... other parameters
    ) -> RequestLiveAttendanceModel {
        return RequestLiveAttendanceModel(
            actualBreakStart: actualBreakStart ?? self.actualBreakStart,
            isBreakStart: isBreakStart ?? self.isBreakStart,
            serverTime: serverTime ?? self.serverTime
            // ... other fields
        )
    }
}
```

**Entity Rules:**
- ✅ Structs (value types) preferred
- ✅ Default initializers with default values
- ✅ `copyWith` extension for immutable updates
- ✅ Equatable conformance for diffing/testing
- ❌ No `import UIKit` or heavy framework dependencies
- ❌ No business logic (pure data)

## Repository Interfaces <!-- 31 -->

```swift
// Domain/Repository/LiveAttendanceRepository.swift
protocol LiveAttendanceRepository {
    func postSubmitCico(
        params: PostSubmitCICOQueryParam,
        companyId: LiveAttendanceCICOPathParam,
        expected: @escaping (Result<RequestLiveAttendanceModel, BaseErrorModel>) -> Void
    )

    func getServerTime(
        params: GetServerTimeQueryParam,
        expected: @escaping (Result<LiveAttendanceServerTimeModel, BaseErrorModel>) -> Void
    )

    func postCicoValidateLocation(
        params: PostCICOValidateLocationQueryParam,
        companyId: LiveAttendanceCICOPathParam,
        expected: @escaping (Result<CICOLocationValidationModel, BaseErrorModel>) -> Void
    )
}
```

**Repository Protocol Rules:**
- ✅ Always use `Result<Model, BaseErrorModel>` in completions
- ✅ Return domain entities (Models), never DTOs (Responses)
- ✅ Method names follow REST convention: `post*`, `get*`, `put*`, `delete*`
- ✅ Params are domain Param objects, not raw dictionaries
- ❌ No implementation details (no Moya, no network code)

## Use Cases <!-- 354 -->

### Legacy UseCase Pattern (Current — In Use)

The codebase uses a 3-parameter base class with separate query params, path params, and a completion callback:

```swift
// Shared/Domain/UseCase/UseCase.swift
typealias PostSubmitCICOUseCaseType = UseCase<PostSubmitCICOQueryParam, LiveAttendanceCICOPathParam, RequestLiveAttendanceModel>

// Usage in ViewModel:
useCase.call(
    queryParams: queryParam,
    pathParams: pathParam,
    expected: { result in /* handle Result<Model, BaseErrorModel> */ }
)
```

The use case type alias pattern: `typealias [Feature]UseCaseType = UseCase<QueryParam, PathParam, ResultModel>`.
`call(queryParams:pathParams:expected:)` is the call site signature.

---

### Modern UseCase Protocol (Target — V2)

Talenta iOS V2 target uses **ONE** clean protocol with nested Params (not yet adopted codebase-wide):

```swift
// Shared/Domain/UseCaseType.swift

/// Base protocol for all UseCases.
/// Each UseCase defines its own nested Params struct.
/// For use cases without parameters, use `typealias Params = Void`
protocol UseCaseProtocol {
    associatedtype Params
    associatedtype Model

    func execute(
        params: Params,
        completion: @escaping (Result<Model, BaseErrorModel>) -> Void
    )
}
```

**Key Benefits:**
- ✅ **Single protocol** - No confusion between multiple protocol types
- ✅ **No naming conflicts** - `UseCaseProtocol` avoids clash with legacy `UseCase` protocol
- ✅ **No param collisions** - `GetEmployeeUseCase.Params` vs `UpdateEmployeeUseCase.Params`
- ✅ **Discoverable** - Autocomplete shows params right from UseCase type
- ✅ **Colocated** - Params definition lives next to the code that uses it
- ✅ **Self-documenting** - All inputs clearly defined in one place
- ✅ **Consistent API** - All use cases have the same `execute(params:completion:)` signature

### UseCase Implementation Patterns

#### Pattern 1: GET with Single ID

```swift
// Domain/UseCase/Employee/GetEmployeeUseCase.swift

final class GetEmployeeUseCase: UseCaseProtocol {
    // MARK: - Params (Nested inside UseCase)
    struct Params {
        let employeeId: String
    }

    // MARK: - Singleton
    private static var _sharedInstance: GetEmployeeUseCase?
    static var sharedInstance: GetEmployeeUseCase {
        if _sharedInstance == nil {
            _sharedInstance = GetEmployeeUseCase()
        }
        return _sharedInstance!
    }

    // MARK: - Dependencies
    private let repository: EmployeeRepository

    // MARK: - Init
    init(repository: EmployeeRepository = EmployeeRepositoryImpl.sharedInstance) {
        self.repository = repository
    }

    // MARK: - Execute
    func execute(
        params: Params,
        completion: @escaping (Result<EmployeeModel, BaseErrorModel>) -> Void
    ) {
        repository.getEmployee(id: params.employeeId, completion: completion)
    }
}
```

**Usage in ViewModel:**
```swift
let params = GetEmployeeUseCase.Params(employeeId: "123")
getEmployeeUseCase.execute(params: params) { result in
    // Handle result
}
```

#### Pattern 2: GET with Multiple Query Parameters

```swift
// Domain/UseCase/Employee/GetEmployeesUseCase.swift

final class GetEmployeesUseCase: UseCaseProtocol {
    // MARK: - Params
    struct Params {
        let page: Int
        let limit: Int
        let departmentId: String?
        let searchQuery: String?

        // Provide default values for convenience
        init(
            page: Int = 1,
            limit: Int = 20,
            departmentId: String? = nil,
            searchQuery: String? = nil
        ) {
            self.page = page
            self.limit = limit
            self.departmentId = departmentId
            self.searchQuery = searchQuery
        }
    }

    // MARK: - Singleton
    private static var _sharedInstance: GetEmployeesUseCase?
    static var sharedInstance: GetEmployeesUseCase {
        if _sharedInstance == nil {
            _sharedInstance = GetEmployeesUseCase()
        }
        return _sharedInstance!
    }

    // MARK: - Dependencies
    private let repository: EmployeeRepository

    // MARK: - Init
    init(repository: EmployeeRepository = EmployeeRepositoryImpl.sharedInstance) {
        self.repository = repository
    }

    // MARK: - Execute
    func execute(
        params: Params,
        completion: @escaping (Result<PaginatedResult<EmployeeModel>, BaseErrorModel>) -> Void
    ) {
        repository.getEmployees(
            page: params.page,
            limit: params.limit,
            departmentId: params.departmentId,
            searchQuery: params.searchQuery,
            completion: completion
        )
    }
}
```

**Usage:**
```swift
// With defaults
let params = GetEmployeesUseCase.Params()

// With custom values
let params = GetEmployeesUseCase.Params(page: 2, limit: 50, departmentId: "eng-001")

getEmployeesUseCase.execute(params: params) { result in ... }
```

#### Pattern 3: POST/PUT with Path ID + Body (Nested Payload)

**Key Pattern:** Separate path identifiers from payload body using nested structs.

```swift
// Domain/UseCase/CICO/PostSubmitCICOUseCase.swift

final class PostSubmitCICOUseCase: UseCaseProtocol {
    // MARK: - Params
    struct Params {
        let companyId: Int          // Path parameter
        let payload: Payload        // Request body

        struct Payload {
            let employeeId: Int
            let scheduleId: Int
            let actualCheckIn: String?
            let actualCheckOut: String?
            let latitude: Double?
            let longitude: Double?
            let media: Data?
            let notes: String?

            init(
                employeeId: Int,
                scheduleId: Int,
                actualCheckIn: String? = nil,
                actualCheckOut: String? = nil,
                latitude: Double? = nil,
                longitude: Double? = nil,
                media: Data? = nil,
                notes: String? = nil
            ) {
                self.employeeId = employeeId
                self.scheduleId = scheduleId
                self.actualCheckIn = actualCheckIn
                self.actualCheckOut = actualCheckOut
                self.latitude = latitude
                self.longitude = longitude
                self.media = media
                self.notes = notes
            }
        }
    }

    // MARK: - Singleton
    private static var _sharedInstance: PostSubmitCICOUseCase?
    static var sharedInstance: PostSubmitCICOUseCase {
        if _sharedInstance == nil {
            _sharedInstance = PostSubmitCICOUseCase()
        }
        return _sharedInstance!
    }

    // MARK: - Dependencies
    private let repository: LiveAttendanceRepository

    // MARK: - Init
    init(repository: LiveAttendanceRepository = LiveAttendanceRepositoryImpl.sharedInstance) {
        self.repository = repository
    }

    // MARK: - Execute
    func execute(
        params: Params,
        completion: @escaping (Result<RequestLiveAttendanceModel, BaseErrorModel>) -> Void
    ) {
        repository.postSubmitCico(
            companyId: params.companyId,
            employeeId: params.payload.employeeId,
            scheduleId: params.payload.scheduleId,
            actualCheckIn: params.payload.actualCheckIn,
            actualCheckOut: params.payload.actualCheckOut,
            latitude: params.payload.latitude,
            longitude: params.payload.longitude,
            media: params.payload.media,
            notes: params.payload.notes,
            completion: completion
        )
    }
}
```

**Usage in ViewModel:**
```swift
let payload = PostSubmitCICOUseCase.Params.Payload(
    employeeId: 123,
    scheduleId: 456,
    latitude: -6.2088,
    longitude: 106.8456,
    media: selfieImageData
)

let params = PostSubmitCICOUseCase.Params(
    companyId: userViewModel.companyId,
    payload: payload
)

postSubmitCICOUseCase.execute(params: params) { [weak self] result in
    switch result {
    case .success(let model):
        self?.emitAction(.navigateToSuccess)
    case .failure(let error):
        self?.emitAction(.showToast(message: error.message))
    }
}
```

#### Pattern 4: UseCase Without Parameters

**Key Pattern:** Use `typealias Params = Void` for use cases that don't need parameters.

```swift
// Domain/UseCase/Auth/GetCurrentUserUseCase.swift

final class GetCurrentUserUseCase: UseCaseProtocol {
    // MARK: - Params
    typealias Params = Void  // No parameters needed

    // MARK: - Singleton
    private static var _sharedInstance: GetCurrentUserUseCase?
    static var sharedInstance: GetCurrentUserUseCase {
        if _sharedInstance == nil {
            _sharedInstance = GetCurrentUserUseCase()
        }
        return _sharedInstance!
    }

    // MARK: - Dependencies
    private let repository: AuthRepository

    // MARK: - Init
    init(repository: AuthRepository = AuthRepositoryImpl.sharedInstance) {
        self.repository = repository
    }

    // MARK: - Execute
    func execute(
        params: Void,
        completion: @escaping (Result<UserModel, BaseErrorModel>) -> Void
    ) {
        repository.getCurrentUser(completion: completion)
    }
}
```

**Usage in ViewModel:**
```swift
// Simple call with unit literal ()
getCurrentUserUseCase.execute(params: ()) { [weak self] result in
    switch result {
    case .success(let user):
        self?.emitAction(.updateUser(user))
    case .failure(let error):
        self?.emitAction(.showError(error.message))
    }
}
```

### Params Pattern Summary

| Operation | Params Structure | Example |
|-----------|-----------------|---------|
| **No params** | `typealias Params = Void` | `useCase.execute(params: ())` |
| **GET (single)** | `Params { id }` | `GetEmployeeUseCase.Params(employeeId: "123")` |
| **GET (list)** | `Params { page, limit, filters... }` | `GetEmployeesUseCase.Params(page: 1, limit: 20)` |
| **POST** | `Params { payload: Payload { fields... } }` | `CreateEmployeeUseCase.Params(payload: ...)` |
| **PUT** | `Params { id, payload: Payload { fields... } }` | `UpdateEmployeeUseCase.Params(employeeId: "123", payload: ...)` |
| **DELETE** | `Params { id }` | `DeleteTaskUseCase.Params(taskId: "456")` |
| **POST (with path)** | `Params { pathId, payload: Payload { ... } }` | `PostSubmitCICOUseCase.Params(companyId: 1, payload: ...)` |

**Naming:** `[HttpMethod][Feature]UseCase`
- GET: `GetCustomFormUseCase`, `GetAttendanceHistoryUseCase`
- POST: `PostSubmitCICOUseCase`, `PostRequestOvertimeUseCase`
- PUT: `PutUpdateProfileUseCase`
- DELETE: `DeleteTaskUseCase`

**Why Nest Params Inside UseCase?**
- No name collisions — `GetEmployeeUseCase.Params` vs `UpdateEmployeeUseCase.Params`
- Discoverable — autocomplete shows params right from the UseCase type
- Colocated — params definition lives next to the code that uses it

## Domain Services <!-- 348 -->

Pure business decisions — no I/O, no side effects, no async. Can be called by both UseCases and ViewModels. See extraction rules in `reference/code-architecture/domain-theory.md`.

### Service Patterns

Talenta iOS uses **two service patterns** depending on complexity:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Struct-based** | Simple, stateless calculations | `LeaveBalanceCalculator` |
| **Protocol + Class** | Complex logic, needs mocking, shared state | `InboxApproveAllService` |

### Pattern 1: Simple Struct-Based Service

For straightforward calculations and validations:

```swift
// Domain/Services/LeaveBalanceCalculator.swift
struct LeaveBalanceCalculator {
    func remainingBalance(for entitlement: LeaveEntitlement) -> Int {
        let pendingDays = entitlement.pendingRequests
            .filter { $0.status == .pending }
            .reduce(0) { $0 + $1.days }

        let remaining = entitlement.annualDays - entitlement.usedDays - pendingDays
        return max(0, remaining)
    }

    func isSufficient(entitlement: LeaveEntitlement, requestedDays: Int) -> Bool {
        remainingBalance(for: entitlement) >= requestedDays
    }
}
```

**Struct Service Rules:**
- ✅ Stateless, value-type semantics
- ✅ Simple calculations and validations
- ✅ Default parameter injection for composition
- ❌ No shared state or dependencies

### Pattern 2: Protocol + Class Service (Recommended for Complex Logic)

For complex business logic that needs mocking, dependency injection, or shared infrastructure:

```swift
// Domain/Services/InboxApproveAllService.swift

/// Protocol defining the service contract
protocol InboxApproveAllService {
    // Eligibility checking
    func shouldShowApproveAllButton(
        inboxType: InboxType,
        selectedStatus: Int,
        isInProgress: Bool
    ) -> Bool

    func validateApproveAllEligibility(
        inboxType: InboxType,
        selectedStatus: Int,
        isInProgress: Bool
    ) -> InboxApproveAllEligibilityResult

    // Progress calculation
    func calculateDisplayProgress(
        serverCurrent: Int,
        serverMax: Int,
        storedTotal: Int
    ) -> InboxProgressDisplayValues

    func isProcessComplete(
        serverCurrent: Int,
        serverMax: Int
    ) -> Bool

    // State recovery
    func determineRecoveryAction(
        inboxType: InboxType,
        currentStatus: Int
    ) -> InboxRecoveryAction

    // Selection mode coordination
    func handleSelectAllToggle(
        currentMode: BulkSelectionMode,
        totalItemCount: Int
    ) -> InboxSelectAllToggleResult

    func calculateSelectedCount(mode: BulkSelectionMode) -> Int

    // Error detection
    func detectErrorType(_ error: BaseErrorModel) -> InboxApproveAllErrorType
    func shouldRecoverAsInProgress(_ error: BaseErrorModel) -> Bool

    // Polling policy
    func pollingInterval(for inboxType: InboxType) -> TimeInterval
    func shouldStopPolling(errorCount: Int) -> Bool

    // Contract building
    func buildApproveAllParameters(
        inboxType: InboxType,
        excludedIds: [Int]
    ) -> [String: Any]
}

/// Implementation with Singleton pattern
final class InboxApproveAllServiceImpl: InboxApproveAllService {

    // MARK: - Singleton
    private static var _sharedInstance: InboxApproveAllServiceImpl?
    static var sharedInstance: InboxApproveAllServiceImpl {
        if _sharedInstance == nil {
            _sharedInstance = InboxApproveAllServiceImpl()
        }
        return _sharedInstance!
    }

    // MARK: - Dependencies
    private let toggleViewModel: ToggleModel
    private let inboxHelper: InboxHelperProtocol

    // MARK: - Configuration
    private let standardPollingInterval: TimeInterval = 5.0
    private let maxConsecutiveErrors: Int = 3

    // MARK: - Init
    init(
        toggleViewModel: ToggleModel = ToggleViewModel(),
        inboxHelper: InboxHelperProtocol = InboxHelper()
    ) {
        self.toggleViewModel = toggleViewModel
        self.inboxHelper = inboxHelper
    }

    // MARK: - Implementation

    func shouldShowApproveAllButton(
        inboxType: InboxType,
        selectedStatus: Int,
        isInProgress: Bool
    ) -> Bool {
        guard inboxType.asyncApprovalWorker > 0 else { return false }
        guard selectedStatus == Constants.NotificationStatusId.pending else { return false }
        guard !isInProgress else { return false }

        let isOnGoingInStorage = inboxHelper.getApproveAllStatus(
            for: inboxType,
            statusId: Constants.NotificationStatusId.pending
        )
        return !isOnGoingInStorage
    }

    func calculateDisplayProgress(
        serverCurrent: Int,
        serverMax: Int,
        storedTotal: Int
    ) -> InboxProgressDisplayValues {
        let displayTotal = serverMax > 0 ? serverMax : storedTotal
        let displayCurrent = min(serverCurrent, displayTotal)
        let percentage = displayTotal > 0 ? Double(displayCurrent) / Double(displayTotal) : 0.0

        return InboxProgressDisplayValues(
            currentCount: displayCurrent,
            totalCount: displayTotal,
            percentage: percentage,
            isServerInitialized: serverMax > 0
        )
    }

    // ... other methods
}

// MARK: - Result Types

enum InboxApproveAllEligibilityResult: Equatable {
    case eligible
    case alreadyInProgress
    case featureDisabled
    case requiresPendingStatus

    var isEligible: Bool { self == .eligible }
}

struct InboxProgressDisplayValues {
    let currentCount: Int
    let totalCount: Int
    let percentage: Double
    let isServerInitialized: Bool
}
```

**Protocol-Based Service Rules:**
- ✅ Protocol for contract, Class for implementation
- ✅ Singleton pattern with `sharedInstance`
- ✅ Dependency injection via init with defaults
- ✅ Result types (enums/structs) for complex return values
- ✅ Testable via protocol mocking
- ✅ Naming: `[Feature]Service` (protocol) + `[Feature]ServiceImpl` (class)

### Services Called from UseCases

```swift
// Domain/UseCases/Leave/SubmitLeaveRequestUseCase.swift
final class SubmitLeaveRequestUseCase: UseCaseProtocol {
    struct Params {
        let entitlement: LeaveEntitlement
        let leaveTypeId: String
        let days: Int
        let startDate: Date
    }

    private let repository: LeaveRepository
    private let balanceCalculator: LeaveBalanceCalculator

    init(
        repository: LeaveRepository = LeaveRepositoryImpl.sharedInstance,
        balanceCalculator: LeaveBalanceCalculator = LeaveBalanceCalculator()
    ) {
        self.repository = repository
        self.balanceCalculator = balanceCalculator
    }

    func execute(params: Params, completion: @escaping (Result<LeaveModel, BaseErrorModel>) -> Void) {
        // Use Service for business logic
        guard balanceCalculator.isSufficient(
            entitlement: params.entitlement,
            requestedDays: params.days
        ) else {
            completion(.failure(BaseErrorModel(message: "Insufficient balance")))
            return
        }

        // Business logic passed, delegate to repository
        repository.submitLeaveRequest(
            leaveTypeId: params.leaveTypeId,
            startDate: params.startDate,
            days: params.days,
            completion: completion
        )
    }
}
```

### Services Called from ViewModels

**IMPORTANT:** ViewModels can call Services directly for pure business logic (no I/O).

```swift
// Presentation/ViewModel/InboxApprovalListViewModel.swift
class InboxApprovalListViewModel: BaseViewModelV2<State, Event, Action> {

    // MARK: - Dependencies
    private let approveAllService: InboxApproveAllService
    private let submitBulkApprovalUseCase: SubmitBulkApprovalUseCase

    init(
        navigator: InboxApprovalListNavigator,
        submitBulkApprovalUseCase: SubmitBulkApprovalUseCase = SubmitBulkApprovalUseCase.sharedInstance,
        approveAllService: InboxApproveAllService = InboxApproveAllServiceImpl.sharedInstance
    ) {
        self.navigator = navigator
        self.submitBulkApprovalUseCase = submitBulkApprovalUseCase
        self.approveAllService = approveAllService
        super.init()
    }

    override func emitEvent(_ event: InboxApprovalListViewModelEvent) {
        switch event {
        case .viewDidLoad:
            handleViewDidLoad()
        case .approveAllButtonTapped:
            handleApproveAll()
        }
    }

    private func handleViewDidLoad() {
        // ViewModel calls Service for UI state decisions
        let shouldShow = approveAllService.shouldShowApproveAllButton(
            inboxType: inboxType,
            selectedStatus: currentStatus,
            isInProgress: isApprovalInProgress
        )

        updateDataState { state in
            state.showApproveAllButton = shouldShow
        }
    }

    private func handleApproveAll() {
        // ViewModel calls Service for eligibility check
        let eligibility = approveAllService.validateApproveAllEligibility(
            inboxType: inboxType,
            selectedStatus: currentStatus,
            isInProgress: isApprovalInProgress
        )

        guard eligibility.isEligible else {
            emitAction(.showToast(message: eligibility.userMessage ?? "Cannot approve"))
            return
        }

        // After validation, call UseCase for I/O
        let params = SubmitBulkApprovalUseCase.Params(
            type: inboxType,
            param: approveAllService.buildApproveAllParameters(
                inboxType: inboxType,
                excludedIds: []
            )
        )

        submitBulkApprovalUseCase.execute(params: params) { [weak self] result in
            // Handle result...
        }
    }
}
```

**ViewModel → Service Pattern:**
- ✅ Call Services for pure logic (eligibility, validation, calculations)
- ✅ Call UseCases for I/O operations (API calls, storage)
- ✅ Services help ViewModels stay focused on orchestration
- ❌ Services never do I/O (that's UseCase territory)

### When to Use Services

| Scenario | Approach |
|----------|----------|
| Simple condition (1-3 lines) | Keep inline in UseCase/ViewModel |
| Complex multi-step validation | Extract to Service |
| Reused across multiple UseCases/ViewModels | Extract to Service |
| Needs independent unit testing | Extract to Service |
| Pure calculation/decision logic | Extract to Service |
| Shared configuration/policies | Extract to Service |

### Service Pattern Decision Matrix

| Requirement | Use Struct | Use Protocol + Class |
|-------------|------------|----------------------|
| Simple calculations | ✅ | ❌ Over-engineering |
| Needs mocking for tests | ❌ | ✅ |
| Has dependencies (toggles, helpers) | ❌ | ✅ |
| Multiple implementations possible | ❌ | ✅ |
| Shared state or configuration | ❌ | ✅ |
| Complex multi-responsibility logic | ❌ | ✅ |

**Naming:** `[Feature][Verb/Noun]Service` — e.g., `InboxApproveAllService`, `LeaveBalanceCalculator`, `AttendanceScheduleResolver`

**Key Principle:** Services contain pure business logic. UseCases orchestrate I/O. ViewModels orchestrate UI.

## Domain Errors <!-- 15 -->

```swift
// Shared/Domain/Entities/BaseErrorModel.swift
struct BaseErrorModel: Error {
    let status: Int?
    let message: String
    let errors: [String: [String]]?
}
```

`BaseErrorModel` is the canonical error type for all UseCase and Repository completions (`Result<Model, BaseErrorModel>`). Repositories map `NetworkError` → `BaseErrorModel` before propagating upward. See `reference/code-architecture/error-handling-impl.md` for full error flow and mapping patterns.

---

## Domain Enums <!-- 32 -->

```swift
// Domain/enum/CICOType.swift
enum CICOType {
    case clockIn
    case clockOut
    case breakStart
    case breakEnd
}

// Domain/enum/IPAddressStatus.swift
enum IPAddressStatus: String {
    case valid = "valid"
    case invalid = "invalid"
    case unknown = "unknown"
}

// Domain/enum/TimeOffMenuType.swift
enum TimeOffMenuType {
    case request
    case history
    case balance
}
```

**Enum Rules:**
- Define business-level constants and states
- Use meaningful names tied to business domain
- Prefer `String` raw values for API interop when needed
- Location: `Domain/enum/`

## Creation Order <!-- 15 -->

When building a new feature's domain layer, create files in this sequence:

```
1. Domain/Entities/[Feature]Model.swift          ← Entity (pure struct)
2. Domain/Repository/[Feature]Repository.swift   ← Repository protocol
3. Domain/UseCase/[Feature]/Get[Feature]UseCase.swift
   Domain/UseCase/[Feature]/Post[Feature]UseCase.swift
   ...                                            ← Use Case(s)
4. Domain/Services/[Feature]Service.swift        ← Domain Service (only if needed)
```

Never create a use case before the repository protocol it depends on.
`EmployeeRepositoryImpl.sharedInstance` used as the default in `init` must already exist at dependency-injection time — but the protocol is what domain depends on.
