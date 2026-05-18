# iOS — Dependency Injection

> Concepts and invariants: `reference/code-architecture/di-theory.md`. This file covers Swift syntax and iOS-specific patterns.

Talenta iOS uses **Manual DI Container + Constructor Injection** pattern — lightweight, explicit, and framework-free.

## Architecture Overview <!-- 25 -->

```
┌─────────────────────────────────────────────────┐
│  App Launch → DIContainer.shared.configure()   │
│  (Production, Dev, Mock environments)           │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴──────────┐
        │                      │
┌───────▼─────────┐   ┌────────▼────────┐
│ Feature Module  │   │ Shared Module   │
│   DI Container  │   │   DI Container  │
│  (TalentaTM)    │   │   (Common)      │
└───────┬─────────┘   └────────┬────────┘
        │                      │
        └──────────┬───────────┘
                   │
        ┌──────────▼──────────┐
        │  Coordinator/       │
        │  ViewModel          │
        │  (Consumes deps)    │
        └─────────────────────┘
```

## Manual DI Container Pattern <!-- 244 -->

**Recommendation:** Use a lightweight manual DI Container per module to centralize dependency creation.

### Shared DI Container

```swift
// Talenta/Shared/DI/SharedDIContainer.swift
final class SharedDIContainer {

    // MARK: - Singleton
    static let shared = SharedDIContainer()
    private init() {}

    // MARK: - Environment
    enum Environment {
        case production
        case development
        case testing
    }

    private(set) var environment: Environment = .production

    func configure(for environment: Environment) {
        self.environment = environment
    }

    // MARK: - Data Layer

    lazy var baseErrorMapper: BaseErrorModelMapper = {
        BaseErrorModelMapper()
    }()

    // MARK: - Core Services

    lazy var networkMonitor: NetworkMonitoring = {
        switch environment {
        case .production, .development:
            return NetworkMonitor.shared
        case .testing:
            return MockNetworkMonitor()
        }
    }()

    lazy var locationManager: TalentaLocationManager = {
        switch environment {
        case .production, .development:
            return LocationManager()
        case .testing:
            return MockLocationManager()
        }
    }()

    lazy var analyticsService: AnalyticsService = {
        switch environment {
        case .production:
            return FirebaseAnalyticsService.shared
        case .development:
            return DebugAnalyticsService()
        case .testing:
            return MockAnalyticsService()
        }
    }()

    // MARK: - Reset (for testing)

    func reset() {
        // Reset all lazy properties by recreating container
        // Used in unit tests between test cases
    }
}
```

### Feature Module DI Container

```swift
// Talenta/Module/TalentaTM/DI/TalentaTMDIContainer.swift
final class TalentaTMDIContainer {

    // MARK: - Singleton
    static let shared = TalentaTMDIContainer()
    private init() {}

    // MARK: - Shared Dependencies
    private let sharedContainer = SharedDIContainer.shared

    // MARK: - Data Layer - DataSources

    lazy var liveAttendanceRemoteDataSource: LiveAttendanceRemoteDataSource = {
        LiveAttendanceRemoteDataSourceImpl()
    }()

    lazy var timeOffRemoteDataSource: TimeOffRemoteDataSource = {
        TimeOffRemoteDataSourceImpl()
    }()

    // MARK: - Data Layer - Mappers

    lazy var requestLiveAttendanceMapper: RequestLiveAttendanceModelMapperType = {
        RequestLiveAttendanceModelMapper()
    }()

    lazy var cicoLocationValidationMapper: CICOLocationValidationModelMapperType = {
        CICOLocationValidationModelMapper()
    }()

    lazy var serverTimeMapper: LiveAttendanceServerTimeModelMapperType = {
        LiveAttendanceServerTimeModelMapper()
    }()

    // MARK: - Data Layer - Repositories

    lazy var liveAttendanceRepository: LiveAttendanceRepository = {
        LiveAttendanceRepositoryImpl(
            remoteDataSource: liveAttendanceRemoteDataSource,
            requestLiveAttendanceMapper: requestLiveAttendanceMapper,
            cicoLocationValidationMapper: cicoLocationValidationMapper,
            serverTimeMapper: serverTimeMapper,
            baseErrorModelMapper: sharedContainer.baseErrorMapper
        )
    }()

    lazy var timeOffRepository: TimeOffRepository = {
        TimeOffRepositoryImpl(
            remoteDataSource: timeOffRemoteDataSource
        )
    }()

    // MARK: - Domain Layer - UseCases

    lazy var postSubmitCICOUseCase: PostSubmitCICOUseCaseType = {
        PostSubmitCICOUseCase(
            repository: liveAttendanceRepository
        )
    }()

    lazy var getCICOLocationValidationUseCase: GetCICOLocationValidationUseCaseType = {
        GetCICOLocationValidationUseCase(
            repository: liveAttendanceRepository
        )
    }()

    lazy var getTimeOffListUseCase: GetTimeOffListUseCaseType = {
        GetTimeOffListUseCase(
            repository: timeOffRepository
        )
    }()

    // MARK: - Domain Layer - Services

    lazy var cicoValidator: CICOValidationService = {
        CICOValidationService()
    }()

    lazy var timeCalculator: TimeCalculationService = {
        TimeCalculationService()
    }()

    // MARK: - Factory Methods (for ViewModels)

    func makeCICOLocationViewModel(
        navigator: CICOLocationNavigator
    ) -> CICOLocationViewModel {
        CICOLocationViewModel(
            navigator: navigator,
            postSubmitCICOUseCase: postSubmitCICOUseCase,
            getCICOLocationValidationUseCase: getCICOLocationValidationUseCase,
            locationManager: sharedContainer.locationManager,
            analyticsService: sharedContainer.analyticsService
        )
    }

    func makeTimeOffListViewModel(
        navigator: TimeOffListNavigator
    ) -> TimeOffListViewModel {
        TimeOffListViewModel(
            navigator: navigator,
            getTimeOffListUseCase: getTimeOffListUseCase,
            analyticsService: sharedContainer.analyticsService
        )
    }

    // MARK: - Reset (for testing)

    func reset() {
        // Force recreation of all lazy properties
        // Called in setUp() of unit tests
    }
}
```

### App Configuration

```swift
// AppDelegate.swift
@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        configureDependencies()

        return true
    }

    private func configureDependencies() {
        #if DEBUG
        // Use development environment for debug builds
        SharedDIContainer.shared.configure(for: .development)
        #else
        // Use production environment for release builds
        SharedDIContainer.shared.configure(for: .production)
        #endif
    }
}
```

### Usage in Coordinator

```swift
// Talenta/Module/TalentaTM/Presentation/Coordinator/CICOCoordinator.swift
class CICOCoordinator: Coordinator {

    private let container = TalentaTMDIContainer.shared

    func showCICOLocation() {
        // ViewModel created by DI Container factory
        let viewModel = container.makeCICOLocationViewModel(navigator: self)
        let viewController = CICOLocationViewController(viewModel: viewModel)

        navigationController.pushViewController(viewController, animated: true)
    }
}

extension CICOCoordinator: CICOLocationNavigator {
    func navigateToSuccess() {
        // Navigation logic
    }
}
```

## Constructor Injection (Fallback Pattern) <!-- 25 -->

For classes **not** managed by DI Container (legacy code, simple utilities), use constructor injection with defaults:

```swift
class CICOLocationViewModel: BaseViewModelV2<...> {
    private let postSubmitCICOUseCase: any PostSubmitCICOUseCaseType
    private let locationManager: TalentaLocationManager

    init(
        navigator: any CICOLocationNavigator,
        postSubmitCICOUseCase: any PostSubmitCICOUseCaseType = TalentaTMDIContainer.shared.postSubmitCICOUseCase,
        locationManager: TalentaLocationManager = SharedDIContainer.shared.locationManager
    ) {
        self.postSubmitCICOUseCase = postSubmitCICOUseCase
        self.locationManager = locationManager
        super.init()
    }
}
```

**When to use:**
- ✅ **DI Container Factory:** New code, complex dependency graphs
- ✅ **Constructor Injection with Defaults:** Legacy code, simple utilities, backward compatibility

## Testing with DI Container <!-- 56 -->

```swift
// TalentaTests/Module/TalentaTM/Presentation/ViewModel/CICOLocationViewModelTest.swift
final class CICOLocationViewModelTest: XCTestCase {

    var sut: CICOLocationViewModel!
    var mockNavigator: MockCICOLocationNavigator!
    var mockPostSubmitCICOUseCase: MockPostSubmitCICOUseCase!
    var mockLocationManager: MockLocationManager!

    override func setUp() {
        super.setUp()

        // Configure test environment
        SharedDIContainer.shared.configure(for: .testing)

        // Create mocks
        mockNavigator = MockCICOLocationNavigator()
        mockPostSubmitCICOUseCase = MockPostSubmitCICOUseCase()
        mockLocationManager = MockLocationManager()

        // Inject mocks via constructor
        sut = CICOLocationViewModel(
            navigator: mockNavigator,
            postSubmitCICOUseCase: mockPostSubmitCICOUseCase,
            getCICOLocationValidationUseCase: MockGetCICOLocationValidationUseCase(),
            locationManager: mockLocationManager,
            analyticsService: MockAnalyticsService()
        )
    }

    override func tearDown() {
        sut = nil
        mockNavigator = nil
        mockPostSubmitCICOUseCase = nil
        mockLocationManager = nil

        super.tearDown()
    }

    func testSubmitCICO_Success() {
        // Arrange
        let expectedResult: Result<RequestLiveAttendanceModel, BaseErrorModel> = .success(mockModel)
        mockPostSubmitCICOUseCase.executeResult = expectedResult

        // Act
        sut.handle(.submitCICO)

        // Assert
        XCTAssertEqual(mockPostSubmitCICOUseCase.executeCallCount, 1)
        XCTAssertTrue(mockNavigator.navigateToSuccessCalled)
    }
}
```

## DI Principles <!-- 12 -->

| Component | Lifecycle | Managed By |
|-----------|-----------|------------|
| **Repositories** | Singleton (lazy) | DI Container |
| **Mappers** | Singleton (lazy) | DI Container |
| **UseCases** | Singleton (lazy) | DI Container |
| **Services** | Singleton (lazy) | DI Container |
| **ViewModels** | Factory (new instance) | DI Container `make*()` methods |
| **Coordinators** | Factory (new instance) | Parent coordinator |
| **ViewControllers** | Factory (new instance) | Coordinator |

## Benefits of Manual DI Container <!-- 13 -->

| Benefit | Description |
|---------|-------------|
| ✅ **Zero Framework Overhead** | No Needle/Swinject code generation or runtime reflection |
| ✅ **Explicit Dependencies** | All dependencies visible in one place per module |
| ✅ **Environment Switching** | Easy to swap prod/dev/test implementations |
| ✅ **Debuggable** | Step through container code, no magic |
| ✅ **Type-Safe** | Compile-time checks, no string-based lookups |
| ✅ **Testable** | Override specific dependencies in tests via constructor injection |
| ✅ **Modular** | Each feature module has own container, clear boundaries |
| ✅ **Lazy Initialization** | Dependencies created only when needed |

## When to Use What? <!-- 19 -->

```swift
// ✅ RECOMMENDED: DI Container factory for ViewModels
let viewModel = TalentaTMDIContainer.shared.makeCICOLocationViewModel(navigator: self)

// ✅ OK: Direct access for UseCases/Repositories (if needed outside container)
let useCase = TalentaTMDIContainer.shared.postSubmitCICOUseCase

// ✅ OK: Constructor injection with container defaults (legacy compatibility)
init(useCase: PostSubmitCICOUseCaseType = TalentaTMDIContainer.shared.postSubmitCICOUseCase)

// ❌ AVOID: Hardcoded singleton instances (not testable)
let useCase = PostSubmitCICOUseCase.sharedInstance

// ❌ AVOID: Creating instances directly in ViewModel
let repository = LiveAttendanceRepositoryImpl()
```

## DI Wrapper (Minimal Setup) <!-- 257 -->

**Advanced Pattern:** Use property wrappers and a registry to minimize boilerplate while keeping type safety.

### Dependency Property Wrappers

```swift
// Talenta/Shared/DI/PropertyWrappers/Injected.swift

/// Property wrapper for singleton dependencies (repositories, use cases, services)
@propertyWrapper
struct Injected<T> {
    private let keyPath: KeyPath<DIContainer, T>

    init(_ keyPath: KeyPath<DIContainer, T>) {
        self.keyPath = keyPath
    }

    var wrappedValue: T {
        DIContainer.shared[keyPath: keyPath]
    }
}

/// Property wrapper for factory dependencies (view models)
@propertyWrapper
struct Factory<T> {
    private let factory: (DIContainer) -> T

    init(_ factory: @escaping (DIContainer) -> T) {
        self.factory = factory
    }

    var wrappedValue: T {
        factory(DIContainer.shared)
    }
}
```

### Streamlined DI Container

```swift
// Talenta/Module/TalentaTM/DI/TalentaTMDIContainer.swift
final class TalentaTMDIContainer {
    static let shared = TalentaTMDIContainer()
    private init() {}

    // MARK: - Shared
    private let shared = SharedDIContainer.shared

    // MARK: - Data Layer (Compact registration)

    lazy var liveAttendanceRemoteDataSource: LiveAttendanceRemoteDataSource =
        LiveAttendanceRemoteDataSourceImpl()

    lazy var requestLiveAttendanceMapper: RequestLiveAttendanceModelMapperType =
        RequestLiveAttendanceModelMapper()

    lazy var cicoLocationValidationMapper: CICOLocationValidationModelMapperType =
        CICOLocationValidationModelMapper()

    lazy var liveAttendanceRepository: LiveAttendanceRepository =
        LiveAttendanceRepositoryImpl(
            remoteDataSource: liveAttendanceRemoteDataSource,
            requestLiveAttendanceMapper: requestLiveAttendanceMapper,
            cicoLocationValidationMapper: cicoLocationValidationMapper,
            baseErrorModelMapper: shared.baseErrorMapper
        )

    // MARK: - Domain Layer (Compact registration)

    lazy var postSubmitCICOUseCase: PostSubmitCICOUseCaseType =
        PostSubmitCICOUseCase(repository: liveAttendanceRepository)

    lazy var getCICOLocationValidationUseCase: GetCICOLocationValidationUseCaseType =
        GetCICOLocationValidationUseCase(repository: liveAttendanceRepository)
}

// MARK: - Factory Extension (Computed Properties)
extension TalentaTMDIContainer {
    func makeCICOLocationViewModel(navigator: CICOLocationNavigator) -> CICOLocationViewModel {
        CICOLocationViewModel(
            navigator: navigator,
            postSubmitCICOUseCase: postSubmitCICOUseCase,
            getCICOLocationValidationUseCase: getCICOLocationValidationUseCase,
            locationManager: shared.locationManager
        )
    }
}
```

### Usage with @Injected Wrapper

**In Coordinator:**
```swift
class CICOCoordinator: Coordinator {
    @Injected(\.postSubmitCICOUseCase) var postSubmitCICOUseCase

    private let container = TalentaTMDIContainer.shared

    func showCICOLocation() {
        // Still use factory for ViewModels (they need fresh instances)
        let viewModel = container.makeCICOLocationViewModel(navigator: self)
        let viewController = CICOLocationViewController(viewModel: viewModel)
        navigationController.pushViewController(viewController, animated: true)
    }
}
```

**In ViewModel (if needed):**
```swift
class CICOLocationViewModel: BaseViewModelV2<...> {
    // Constructor injection still recommended for testability
    private let postSubmitCICOUseCase: PostSubmitCICOUseCaseType
    private let locationManager: TalentaLocationManager

    init(
        navigator: CICOLocationNavigator,
        postSubmitCICOUseCase: PostSubmitCICOUseCaseType,
        getCICOLocationValidationUseCase: GetCICOLocationValidationUseCaseType,
        locationManager: TalentaLocationManager
    ) {
        self.postSubmitCICOUseCase = postSubmitCICOUseCase
        self.locationManager = locationManager
        super.init()
    }
}
```

### Alternative: Builder Pattern

For even more concise setup with type inference:

```swift
// Talenta/Shared/DI/DIBuilder.swift
final class DIBuilder {
    static func buildTalentaTM() -> TalentaTMDIContainer {
        let container = TalentaTMDIContainer()

        // Auto-wiring with keypaths
        container.configure { c in
            // Data layer
            c.register { LiveAttendanceRemoteDataSourceImpl() }
            c.register { RequestLiveAttendanceModelMapper() }
            c.register {
                LiveAttendanceRepositoryImpl(
                    remoteDataSource: c.resolve(),
                    requestLiveAttendanceMapper: c.resolve(),
                    baseErrorModelMapper: c.resolve()
                )
            }

            // Domain layer
            c.register { PostSubmitCICOUseCase(repository: c.resolve()) }
        }

        return container
    }
}
```

### Recommended Approach: Lazy Properties (Simplest)

**Best balance of simplicity and explicitness:**

```swift
final class TalentaTMDIContainer {
    static let shared = TalentaTMDIContainer()
    private init() {}

    // One-liner registrations with lazy initialization
    lazy var postSubmitCICOUseCase: PostSubmitCICOUseCaseType =
        PostSubmitCICOUseCase(repository: liveAttendanceRepository)

    lazy var liveAttendanceRepository: LiveAttendanceRepository =
        LiveAttendanceRepositoryImpl(
            remoteDataSource: liveAttendanceRemoteDataSource,
            requestLiveAttendanceMapper: requestLiveAttendanceMapper,
            baseErrorModelMapper: SharedDIContainer.shared.baseErrorMapper
        )

    lazy var liveAttendanceRemoteDataSource: LiveAttendanceRemoteDataSource =
        LiveAttendanceRemoteDataSourceImpl()

    lazy var requestLiveAttendanceMapper: RequestLiveAttendanceModelMapperType =
        RequestLiveAttendanceModelMapper()
}
```

**Why this is recommended:**
- ✅ No property wrapper boilerplate
- ✅ One-line registration
- ✅ Type-safe with auto-completion
- ✅ Lazy initialization built-in
- ✅ Explicit dependency graph visible
- ✅ Easy to debug (step through property access)
- ✅ No protocol registration needed
- ✅ Works with any Swift version

### Comparison

| Approach | Setup Lines | Type Safety | Testability | Readability |
|----------|-------------|-------------|-------------|-------------|
| **Lazy Properties** ⭐ | Minimal | ✅ Compile-time | ✅ Constructor injection | ⭐⭐⭐⭐⭐ |
| **@Injected Wrapper** | Medium | ✅ Compile-time | ⚠️ Harder to mock | ⭐⭐⭐⭐ |
| **Builder Pattern** | More setup | ✅ Compile-time | ✅ Good | ⭐⭐⭐ |
| **Registry Pattern** | Most setup | ⚠️ Runtime casts | ⚠️ Complex | ⭐⭐ |

**Recommendation:** Use **Lazy Properties** (7.8.5) for maximum clarity with minimal boilerplate.

### Simplified Example: Complete Module

```swift
// Talenta/Module/TalentaTM/DI/TalentaTMDIContainer.swift
final class TalentaTMDIContainer {
    static let shared = TalentaTMDIContainer()
    private init() {}

    // Shared dependencies
    private let shared = SharedDIContainer.shared

    // Data Layer - one-liner registrations
    lazy var liveAttendanceDataSource: LiveAttendanceRemoteDataSource = LiveAttendanceRemoteDataSourceImpl()
    lazy var attendanceMapper: RequestLiveAttendanceModelMapperType = RequestLiveAttendanceModelMapper()
    lazy var validationMapper: CICOLocationValidationModelMapperType = CICOLocationValidationModelMapper()

    lazy var liveAttendanceRepository: LiveAttendanceRepository = LiveAttendanceRepositoryImpl(
        remoteDataSource: liveAttendanceDataSource,
        requestLiveAttendanceMapper: attendanceMapper,
        cicoLocationValidationMapper: validationMapper,
        baseErrorModelMapper: shared.baseErrorMapper
    )

    // Domain Layer - one-liner registrations
    lazy var postSubmitCICOUseCase: PostSubmitCICOUseCaseType = PostSubmitCICOUseCase(repository: liveAttendanceRepository)
    lazy var getValidationUseCase: GetCICOLocationValidationUseCaseType = GetCICOLocationValidationUseCase(repository: liveAttendanceRepository)
    lazy var cicoValidator: CICOValidationService = CICOValidationService()

    // Factory for ViewModels
    func makeCICOLocationViewModel(navigator: CICOLocationNavigator) -> CICOLocationViewModel {
        CICOLocationViewModel(
            navigator: navigator,
            postSubmitCICOUseCase: postSubmitCICOUseCase,
            getCICOLocationValidationUseCase: getValidationUseCase,
            locationManager: shared.locationManager,
            validator: cicoValidator
        )
    }
}
```

**Benefits:**
- **~70% less boilerplate** compared to manual singleton pattern
- **Still explicit** - all dependencies visible at a glance
- **Type-safe** - compile-time checks, autocomplete works
- **Lazy** - dependencies created only when needed
- **Testable** - constructor injection still works for tests
- **Zero magic** - no code generation, no runtime reflection
