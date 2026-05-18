# iOS — Data Layer

> Concepts and invariants: `reference/code-architecture/data-theory.md`. This file covers Swift syntax and iOS-specific patterns.

Implements Domain protocols. Handles all I/O: network, storage, caching.

## Dependency Rule <!-- 13 -->

Data depends on Domain only. It never imports from Presentation or UI.

**Allowed:** `Foundation`, Moya, `MoyaProvider`, `JSONDecoder`, `UserDefaults`, `CoreData`, `NWPathMonitor`, any persistence or networking library.

**Forbidden:**
- `import UIKit` — UI types must not appear in data layer files
- Any `ViewModel`, `ViewController`, `Coordinator`, or `Navigator` type
- Any presentation-layer import — data layer must not know how results are displayed

---

## DTOs <!-- 69 -->

iOS calls these **Response Models** (`*Response` / `*ResponseData` structs). Same contract as core — raw API shape, all fields optional (`?`), `CodingKeys` for snake_case mapping, no business logic. Never escape the Data layer.

API response models. Separate from domain entities.

```swift
// Data/Models/LiveAttendance/RequestLiveAttendanceResponse.swift
struct RequestLiveAttendanceResponse: Decodable {
    let status: Bool?
    let message: String?
    let data: RequestLiveAttendanceResponseData?
}

struct RequestLiveAttendanceResponseData: Decodable {
    let actualBreakStart: String?
    let isBreakStart: Bool?
    let isBreakEnd: Bool?
    let currentShiftDate: String?
    let currentShiftName: String?
    let currentShiftLabel: String?
    let currentShiftScIn: String?
    let currentShiftScOut: String?
    let actualCheckIn: String?
    let actualCheckOut: String?
    let faceRecogAccuracy: Double?
    let livenessAccuracy: Double?
    let serverTime: String?
    let useGracePeriod: Bool?
    let clockInDispensationDuration: Int?
    let clockOutDispensationDuration: Int?
    let processedAsync: Bool?
    let errorCase: String?
    let ipAddressStatus: Bool?
    let validIpAddress: Bool?

    enum CodingKeys: String, CodingKey {
        case actualBreakStart = "actual_break_start"
        case isBreakStart = "is_break_start"
        case isBreakEnd = "is_break_end"
        case currentShiftDate = "current_shift_date"
        case currentShiftName = "current_shift_name"
        case currentShiftLabel = "current_shift_label"
        case currentShiftScIn = "current_shift_sc_in"
        case currentShiftScOut = "current_shift_sc_out"
        case actualCheckIn = "actual_check_in"
        case actualCheckOut = "actual_check_out"
        case faceRecogAccuracy = "face_recog_accuracy"
        case livenessAccuracy = "liveness_accuracy"
        case serverTime = "server_time"
        case useGracePeriod = "use_grace_period"
        case clockInDispensationDuration = "clock_in_dispensation_duration"
        case clockOutDispensationDuration = "clock_out_dispensation_duration"
        case processedAsync = "processed_async"
        case errorCase = "error_case"
        case ipAddressStatus = "ip_address_status"
        case validIpAddress = "valid_ip_address"
    }
}
```

**Response Model Rules:**
- Only conform to `Decodable` (or `Encodable` for POST bodies)
- Field names match API JSON keys via `CodingKeys`
- All fields optional (`?`) — gracefully handle missing data
- Nested API objects get their own Response struct
- Response models never escape Data layer
- Standard wrapper: `status`, `message`, `data` structure

## Data Sources <!-- 59 -->

Abstract the data origin (remote API, local storage, cache).

```swift
// Data/DataSource/Remote/LiveAttendanceRemoteDataSource.swift
protocol LiveAttendanceRemoteDataSource {
    func postSubmitCico(
        params: [String: Any],
        companyId: Int,
        config: TMRequestConfig?,
        completion: @escaping (APIResult<RequestLiveAttendanceResponse>) -> Void
    )

    func getServerTime(
        params: [String: Any],
        config: TMRequestConfig?,
        completion: @escaping (APIResult<LiveAttendanceServerTimeResponse>) -> Void
    )
}

// Data/DataSource/Remote/LiveAttendanceRemoteDataSourceImpl.swift
class LiveAttendanceRemoteDataSourceImpl: LiveAttendanceRemoteDataSource {
    private let provider: MoyaProvider<TimeManagementAPI>

    init(provider: MoyaProvider<TimeManagementAPI> = MoyaProvider<TimeManagementAPI>()) {
        self.provider = provider
    }

    func postSubmitCico(
        params: [String: Any],
        companyId: Int,
        config: TMRequestConfig?,
        completion: @escaping (APIResult<RequestLiveAttendanceResponse>) -> Void
    ) {
        provider.request(.postSubmitCico(params: params, companyId: companyId, config: config)) { result in
            switch result {
            case .success(let response):
                do {
                    let decoded = try JSONDecoder().decode(RequestLiveAttendanceResponse.self, from: response.data)
                    completion(.success(decoded))
                } catch {
                    completion(.error(TalentaBaseError(message: error.localizedDescription)))
                }
            case .failure(let error):
                completion(.error(TalentaBaseError(message: error.localizedDescription)))
            }
        }
    }
}
```

**DataSource Rules:**
- Protocol for abstraction, Impl for implementation
- Takes raw params as `[String: Any]` (converted from domain Params)
- Returns `APIResult<ResponseType>` (custom result enum)
- Uses Moya for HTTP requests
- Error handling: catch decode + network errors

## Mappers <!-- 162 -->

**CRITICAL:** Mappers belong in the **Data Layer**, not Domain Layer.

### Why Mappers Are in Data Layer

Mappers transform API Response models (Data Layer DTOs) into Domain Entities (Domain Layer models).

| Principle | Explanation |
|-----------|-------------|
| **Dependency Rule** | Data layer depends on Domain, not vice versa. Mappers convert `Response` → `Entity`, so they live in Data layer where both types are visible. |
| **Implementation Detail** | How we convert API JSON to domain models is an implementation detail, not business logic. |
| **Framework Dependency** | Mappers use `Codable`, optional unwrapping extensions (`.orEmpty()`, `.orZero()`), and API-specific parsing — these are infrastructure concerns. |
| **Domain Independence** | Domain layer must be pure Swift with zero framework dependencies. Domain shouldn't know about Response models or JSON parsing. |

### Clean Architecture Flow

```
API Response (Data) ──Mapper (Data)──> Domain Entity (Domain) ──> UseCase (Domain)
```

**Correct:** Data layer imports Domain entities, uses Mappers to convert Response → Entity
**Wrong:** Domain layer imports Response models from Data layer (violates dependency rule!)

### Basic Mapper Pattern

```swift
// Data/Mapper/RequestLiveAttendanceModelMapper.swift
protocol RequestLiveAttendanceModelMapperType {
    func fromResponseToModel(from response: RequestLiveAttendanceResponseData) -> RequestLiveAttendanceModel
    func fromModelToResponse(from model: RequestLiveAttendanceModel) -> RequestLiveAttendanceResponseData
}

class RequestLiveAttendanceModelMapper: RequestLiveAttendanceModelMapperType {

    func fromResponseToModel(from response: RequestLiveAttendanceResponseData) -> RequestLiveAttendanceModel {
        return RequestLiveAttendanceModel(
            actualBreakStart: response.actualBreakStart.orEmpty(),
            isBreakStart: response.isBreakStart.orFalse(),
            isBreakEnd: response.isBreakEnd.orFalse(),
            currentShiftDate: response.currentShiftDate.orEmpty(),
            currentShiftName: response.currentShiftName.orEmpty(),
            actualCheckIn: response.actualCheckIn.orEmpty(),
            actualCheckOut: response.actualCheckOut.orEmpty(),
            faceRecogAccuracy: response.faceRecogAccuracy.orDefault(with: -1),
            serverTime: response.serverTime.orEmpty(),
            processedAsync: response.processedAsync.orFalse(),
            ipAddressStatus: response.ipAddressStatus.orFalse()
        )
    }

    func fromModelToResponse(from model: RequestLiveAttendanceModel) -> RequestLiveAttendanceResponseData {
        return RequestLiveAttendanceResponseData(
            actualBreakStart: model.actualBreakStart,
            isBreakStart: model.isBreakStart,
            isBreakEnd: model.isBreakEnd,
            currentShiftDate: model.currentShiftDate,
            currentShiftName: model.currentShiftName,
            actualCheckIn: model.actualCheckIn,
            actualCheckOut: model.actualCheckOut,
            faceRecogAccuracy: model.faceRecogAccuracy,
            serverTime: model.serverTime,
            processedAsync: model.processedAsync,
            ipAddressStatus: model.ipAddressStatus
        )
    }
}
```

### Composable Mappers

Mappers compose via injection — a parent mapper depends on child mappers for nested objects:

```swift
// Data/Mapper/EmployeeMapper.swift
protocol EmployeeMapping {
    func toDomain(_ dto: EmployeeDTO) -> Employee
    func toRequest(_ employee: Employee) -> UpdateEmployeeRequest
}

class EmployeeMapper: EmployeeMapping {
    private let departmentMapper: DepartmentMapping

    init(departmentMapper: DepartmentMapping = DepartmentMapper()) {
        self.departmentMapper = departmentMapper
    }

    func toDomain(_ dto: EmployeeDTO) -> Employee {
        Employee(
            id: dto.id,
            name: dto.fullName,
            email: dto.emailAddress,
            department: departmentMapper.toDomain(dto.department), // delegates to child
            joinDate: ISO8601DateFormatter().date(from: dto.joinedAt) ?? .now
        )
    }

    func toRequest(_ employee: Employee) -> UpdateEmployeeRequest {
        UpdateEmployeeRequest(
            fullName: employee.name,
            emailAddress: employee.email,
            departmentId: employee.department.id
        )
    }
}
```

### When Business Logic Appears in Mapping

❌ **Wrong:** Complex validation in Mapper
```swift
// Data/Mapper/CustomFormMapper.swift
static func map(_ response: CustomFormResponse) -> CustomFormModel {
    // ❌ This is business logic, not just mapping!
    let isValid = response.fields.allSatisfy { $0.isRequired && !$0.value.isEmpty }
    let canSubmit = isValid && response.status == "draft"

    return CustomFormModel(id: response.id.orZero(), isValid: isValid, canSubmit: canSubmit)
}
```

✅ **Correct:** Extract business logic to Domain Service or UseCase
```swift
// Data/Mapper — Simple transformation only
static func map(_ response: CustomFormResponse) -> CustomFormModel {
    return CustomFormModel(
        id: response.id.orZero(),
        fields: response.fields.map { CustomFormFieldModel.from($0) }
    )
}

// Domain/Service — Business logic
class CustomFormValidator {
    func validate(_ form: CustomFormModel) -> Bool {
        return form.fields.allSatisfy { $0.isRequired && !$0.value.isEmpty }
    }

    func canSubmit(_ form: CustomFormModel) -> Bool {
        return validate(form) && form.status == .draft
    }
}
```

**Mapper Rules:**
- One mapper per Response-Model pair: `RequestLiveAttendanceModelMapper`, `AttendanceScheduleModelMapper`
- Protocol-based: `[Name]ModelMapperType` protocol + `[Name]ModelMapper` class
- Use safe unwrapping: `.orEmpty()`, `.orFalse()`, `.orZero()`, `.orDefault(with:)`
- Bidirectional when needed: `fromResponseToModel` and `fromModelToResponse`
- Injected into repositories for testability
- Default parameter injection: `init(childMapper: ChildMapping = ChildMapper())`
- **No business logic** — only data transformation

**Why Protocol-based?**

| Protocol-based (Talenta) | Static enum/struct |
|---------------------------|---------------------|
| ✅ Mock in repository tests — true isolation | Repository tests implicitly test mapper too |
| ✅ Swap mapping strategies (API versioning) | Fixed mapping logic |
| ✅ Composable via DI — inject child mappers | Tightly coupled static calls |
| ✅ Consistent with architecture (injectable) | Simpler for trivial mappers |
| ✅ Testable in isolation | More boilerplate |

## Repository Implementation <!-- 74 -->

Repositories inject **mappers** and **datasources**, implement **domain protocols**.

```swift
// Data/RepositoriesImpl/LiveAttendanceRepositoryImpl.swift
class LiveAttendanceRepositoryImpl: LiveAttendanceRepository {
    // Singleton
    private static var _sharedInstance: LiveAttendanceRepositoryImpl?
    static var sharedInstance: LiveAttendanceRepositoryImpl {
        if _sharedInstance == nil {
            _sharedInstance = LiveAttendanceRepositoryImpl()
        }
        return _sharedInstance!
    }

    // Dependencies
    private let remoteDataSource: any LiveAttendanceRemoteDataSource
    private let requestLiveAttendanceMapper: any RequestLiveAttendanceModelMapperType
    private let cicoLocationValidationMapper: any CICOLocationValidationModelMapperType
    private let serverTimeMapper: any LiveAttendanceServerTimeModelMapperType
    private let baseErrorModelMapper: BaseErrorModelMapper

    init(
        remoteDataSource: any LiveAttendanceRemoteDataSource = LiveAttendanceRemoteDataSourceImpl(),
        requestLiveAttendanceMapper: any RequestLiveAttendanceModelMapperType = RequestLiveAttendanceModelMapper(),
        cicoLocationValidationMapper: any CICOLocationValidationModelMapperType = CICOLocationValidationModelMapper(),
        serverTimeMapper: any LiveAttendanceServerTimeModelMapperType = LiveAttendanceServerTimeModelMapper(),
        baseErrorModelMapper: BaseErrorModelMapper = BaseErrorModelMapper()
    ) {
        self.remoteDataSource = remoteDataSource
        self.requestLiveAttendanceMapper = requestLiveAttendanceMapper
        self.cicoLocationValidationMapper = cicoLocationValidationMapper
        self.serverTimeMapper = serverTimeMapper
        self.baseErrorModelMapper = baseErrorModelMapper
    }

    func postSubmitCico(
        params: PostSubmitCICOQueryParam,
        companyId: LiveAttendanceCICOPathParam,
        expected: @escaping (Result<RequestLiveAttendanceModel, BaseErrorModel>) -> Void
    ) {
        remoteDataSource.postSubmitCico(
            params: params.toDictionary().orEmpty(),
            companyId: companyId.companyId.orZero(),
            config: nil
        ) { [weak self] result in
            guard let self = self else { return }

            switch result {
            case .success(let response):
                if let data = response.data {
                    let model = self.requestLiveAttendanceMapper.fromResponseToModel(from: data)
                    expected(.success(model))
                } else {
                    expected(.failure(BaseErrorModel(message: "No data available")))
                }
            case .error(let error):
                expected(.failure(self.baseErrorModelMapper.fromResponseToModel(from: error)))
            }
        }
    }
}
```

**Repository Rules:**
- Singleton pattern for shared instances
- Inject mappers via constructor with default parameters
- Inject datasources via constructor with default parameters
- Convert domain Params → dictionary for datasource
- Use mappers to convert Response → Domain Model
- Map errors to `BaseErrorModel`
- Return `Result<Model, BaseErrorModel>` via completion

## HTTP Client <!-- 62 -->

Talenta iOS uses **Moya** for type-safe networking.

```swift
// Shared/Network/API/TimeManagementAPI.swift
enum TimeManagementAPI {
    case postSubmitCico(params: [String: Any], companyId: Int, config: TMRequestConfig?)
    case getServerTime(params: [String: Any], config: TMRequestConfig?)
    case postCicoValidateLocation(params: [String: Any], companyId: Int, config: TMRequestConfig?)
}

extension TimeManagementAPI: TargetType {
    var baseURL: URL {
        return URL(string: AppEnvironment.shared.baseURL)!
    }

    var path: String {
        switch self {
        case .postSubmitCico(_, let companyId, _):
            return "/api/v1/companies/\(companyId)/live-attendance"
        case .getServerTime:
            return "/api/v1/server-time"
        case .postCicoValidateLocation(_, let companyId, _):
            return "/api/v1/companies/\(companyId)/live-attendance/validate-location"
        }
    }

    var method: Moya.Method {
        switch self {
        case .postSubmitCico, .postCicoValidateLocation:
            return .post
        case .getServerTime:
            return .get
        }
    }

    var task: Task {
        switch self {
        case .postSubmitCico(let params, _, _), .postCicoValidateLocation(let params, _, _):
            return .requestParameters(parameters: params, encoding: JSONEncoding.default)
        case .getServerTime(let params, _):
            return .requestParameters(parameters: params, encoding: URLEncoding.default)
        }
    }

    var headers: [String: String]? {
        return [
            "Content-Type": "application/json",
            "Authorization": "Bearer \(StorageHelper.getStringValue(key: .accessToken).orEmpty())"
        ]
    }
}
```

**Moya Pattern:**
- Enum cases for endpoints
- Conform to `TargetType` protocol
- Use `.requestParameters` for body/query
- Headers include auth tokens from storage
- MoyaProvider handles HTTP requests

## Advanced Repository Patterns <!-- 99 -->

### Offline Support with Cache Fallback

Use `NWPathMonitor` to check connectivity, fall back to cache when offline:

```swift
import Network

// Data/RepositoriesImpl/[Feature]RepositoryImpl.swift
final class AttendanceRepositoryImpl: AttendanceRepository {

    func getSchedule(
        param: GetAttendanceScheduleParam?,
        completion: @escaping (Result<ScheduleModel, BaseErrorModel>) -> Void
    ) {
        guard networkMonitor.isConnected else {
            if let cached = cacheManager.loadCachedSchedule() {
                completion(.success(cached))
            } else {
                completion(.failure(BaseErrorModel(message: "No internet connection.")))
            }
            return
        }

        dataSource.getSchedule(params: param?.toDictionary()) { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .success(let response):
                guard let data = response.data else {
                    completion(.failure(BaseErrorModel(message: "No data available")))
                    return
                }
                let model = self.mapper.map(from: data)
                self.cacheManager.cacheSchedule(model)
                completion(.success(model))
            case .error(let error):
                completion(.failure(self.baseErrorMapper.fromResponseToModel(from: error)))
            }
        }
    }
}
```

**Rules:**
- Inject `NetworkMonitorProtocol` and `CacheManagerProtocol` for testability
- Cache on successful fetch; serve cache when offline
- Return a clear error only when offline AND no cache exists

### Parallel Requests with DispatchGroup

Combine multiple independent API calls into a single repository method:

```swift
// Data/RepositoriesImpl/DashboardRepositoryImpl.swift
final class DashboardRepositoryImpl: DashboardRepository {

    func getDashboardData(
        completion: @escaping (Result<DashboardDataModel, BaseErrorModel>) -> Void
    ) {
        var attendance: AttendanceModel?
        var announcements: [AnnouncementModel] = []
        var firstError: BaseErrorModel?
        let group = DispatchGroup()

        group.enter()
        attendanceDataSource.getToday { result in
            defer { group.leave() }
            switch result {
            case .success(let r): attendance = r.data.map { self.attendanceMapper.map(from: $0) }
            case .error(let e): firstError = self.baseErrorMapper.fromResponseToModel(from: e)
            }
        }

        group.enter()
        announcementDataSource.getList { result in
            defer { group.leave() }
            if case .success(let r) = result {
                announcements = (r.data ?? []).map { self.announcementMapper.map(from: $0) }
            }
        }

        group.notify(queue: .main) {
            if let error = firstError, attendance == nil {
                completion(.failure(error))
            } else {
                completion(.success(DashboardDataModel(attendance: attendance, announcements: announcements)))
            }
        }
    }
}
```

**Rules:**
- Use `DispatchGroup` for parallel independent calls
- `defer { group.leave() }` ensures leave is always called
- Decide on failure strategy: fail-fast (any error fails all) or partial success (return what you have)
- Call `group.notify(queue: .main)` to deliver result on main thread

## Creation Order <!-- 14 -->

When building a new feature's data layer, create files in this sequence:

```
1. Data/Models/[Feature]/[Feature]Response.swift           ← DTO (Response struct, Decodable)
2. Data/Mapper/[Feature]ModelMapper.swift                  ← Mapper (protocol + class)
3. Data/DataSource/Remote/[Feature]RemoteDataSource.swift  ← DataSource protocol
   Data/DataSource/Remote/[Feature]RemoteDataSourceImpl.swift ← DataSource implementation
4. Data/RepositoriesImpl/[Feature]RepositoryImpl.swift     ← Repository implementation
```

Never create a repository implementation before the data source it depends on.

## Layer Invariants <!-- 7 -->

- Import from domain layer only — never from presentation, ViewController, ViewModel, or Navigator files
- Raw transport errors (`TalentaBaseError`, `MoyaError`) never propagate upward — `RepositoryImpl` maps them to `BaseErrorModel` before calling the completion handler
- `*Response` and `*ResponseData` structs never cross into the domain layer — mappers (`fromResponseToModel`) are the boundary
- All `*RepositoryImpl` files conform to a domain protocol — no concrete type is referenced from outside the data layer
- `MoyaProvider` and `JSONDecoder` live only in DataSource implementations — never in Repository or Domain files
