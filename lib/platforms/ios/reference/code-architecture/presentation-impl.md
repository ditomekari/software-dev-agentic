# iOS — Presentation Layer

> Concepts and invariants: `reference/code-architecture/presentation-theory.md`. This file covers Swift syntax and iOS-specific patterns.

## State Management <!-- 81 -->

Talenta iOS uses **BaseViewModelV2** with generic State/Event/Action pattern.

### State Protocol

```swift
// Shared/Domain/Base/ViewModelState.swift
protocol ViewModelState {
    static var initial: Self { get }
}
```

### State Implementation

```swift
// Presentation/ViewModel/CICOLocation/CICOLocationViewModelState.swift
struct CICOLocationViewModelState: ViewModelState {
    var nextButtonIsEnable: Bool
    var mapViewCameraPosition: CLLocation?
    var updateLocationInfo: CLLocation?
    var actionContainerIsHidden: Bool
    var submitButtonTitle: String
    var appBarTitle: String
    var isLoading: Bool

    static var initial: CICOLocationViewModelState {
        return CICOLocationViewModelState(
            nextButtonIsEnable: false,
            mapViewCameraPosition: nil,
            updateLocationInfo: nil,
            actionContainerIsHidden: false,
            submitButtonTitle: "",
            appBarTitle: "",
            isLoading: false
        )
    }
}
```

### Event Protocol

```swift
// Shared/Domain/Base/ViewModelEvent.swift
protocol ViewModelEvent {}
```

### Event Implementation

```swift
// Presentation/ViewModel/CICOLocation/CICOLocationViewModelEvent.swift
enum CICOLocationViewModelEvent: ViewModelEvent {
    case viewDidLoad
    case submitButtonTapped
    case reloadLocationTapped
    case backButtonTapped
    case openCameraForSelfie
}
```

### Action Protocol

```swift
// Shared/Domain/Base/ViewModelAction.swift
protocol ViewModelAction {}
```

### Action Implementation

```swift
// Presentation/ViewModel/CICOLocation/CICOLocationViewModelAction.swift
enum CICOLocationViewModelAction: ViewModelAction {
    case showToast(message: String)
    case showLoading
    case hideLoading
    case openCamera
    case navigateToSuccess
    case navigationItemRightBarButtonItemRemoveAnimation
}
```

## BaseViewModelV2 <!-- 89 -->

Generic base class for all ViewModels with reactive state management.

```swift
// Shared/Domain/Base/BaseViewModelV2.swift
class BaseViewModelV2<State: ViewModelState, Event: ViewModelEvent, Action: ViewModelAction> {

    // MARK: - State Management
    let stateRelay = BehaviorRelay<State>(value: State.initial)

    // MARK: - Lifecycle
    let disposeBag = DisposeBag()

    // MARK: - Action Management
    let actionSubject = PublishSubject<Action>()
    let commonActionSubject = PublishSubject<CommonViewModelAction>()

    // MARK: - Public Reactive Interfaces
    lazy var stateDriver: Driver<State> = {
        return stateRelay.asDriver()
    }()

    lazy var actionDriver: Driver<Action> = {
        return actionSubject.asDriverOnErrorJustComplete()
    }()

    lazy var commonActionDriver: Driver<CommonViewModelAction> = {
        return commonActionSubject.asDriverOnErrorJustComplete()
    }()

    // MARK: - Init
    init() {
        setBinders()
    }

    // MARK: - Overridable

    /// Override to handle events from View
    func emitEvent(_ event: Event) {
        // Subclasses override
    }

    /// Override to setup reactive bindings
    func setBinders() {
        // Subclasses override
    }

    // MARK: - State Updates

    /// Update state with builder closure
    func updateDataState(builder: (inout State) -> Void) {
        var state = stateRelay.value
        builder(&state)
        stateRelay.accept(state)
    }

    /// Update state with builder closure (alternative)
    func updateDataStateWith(builder: (inout State?) -> Void) {
        var state: State? = stateRelay.value
        builder(&state)
        if let updatedState = state {
            stateRelay.accept(updatedState)
        }
    }

    // MARK: - Action Emission

    /// Emit custom action
    func emitAction(_ action: Action) {
        actionSubject.onNext(action)
    }

    /// Emit common action
    func emitCommonAction(_ action: CommonViewModelAction) {
        commonActionSubject.onNext(action)
    }
}
```

**BaseViewModelV2 Pattern:**
- Generic over `State`, `Event`, `Action`
- State in `BehaviorRelay<State>` for reactive updates
- `stateDriver` exposes state as Driver (main thread, no errors)
- `actionDriver` exposes custom actions
- `commonActionDriver` exposes standard actions (toast, loading)
- Subclasses override `emitEvent(_ event:)` for user interactions
- Subclasses override `setBinders()` for RxSwift bindings

## Concrete ViewModel <!-- 129 -->

```swift
// Presentation/ViewModel/CICOLocation/CICOLocationViewModel.swift
class CICOLocationViewModel: BaseViewModelV2<
    CICOLocationViewModelState,
    CICOLocationViewModelEvent,
    CICOLocationViewModelAction
> {
    // MARK: - DEPENDENCIES
    private weak var navigator: (any CICOLocationNavigator)?
    private let locationManager: TalentaLocationManager
    private let postSubmitCICOUseCase: PostSubmitCICOUseCase
    private let postCICOValidateLocationUseCase: PostCICOValidateLocationUseCase
    private let userViewModel: UserModel

    // MARK: - DATA
    private let currentLocationRelay = BehaviorRelay<CLLocation?>(value: nil)
    private var selfieImage: Data?
    private var notes = ""

    // MARK: - INIT
    init(
        navigator: any CICOLocationNavigator,
        displayMode: CICOLocationDisplayMode,
        type: CICOType,
        scheduleData: AttendanceScheduleModel?,
        currentLocation: CLLocation?,
        mainScheduler: SchedulerType = MainScheduler.instance,
        locationManager: TalentaLocationManager = LocationManager(),
        postSubmitCICOUseCase: PostSubmitCICOUseCase = PostSubmitCICOUseCase.sharedInstance,
        postCICOValidateLocationUseCase: PostCICOValidateLocationUseCase = PostCICOValidateLocationUseCase.sharedInstance,
        userViewModel: UserModel = UserViewModel()
    ) {
        self.navigator = navigator
        self.locationManager = locationManager
        self.postSubmitCICOUseCase = postSubmitCICOUseCase
        self.postCICOValidateLocationUseCase = postCICOValidateLocationUseCase
        self.userViewModel = userViewModel
        self.currentLocationRelay.accept(currentLocation)

        super.init()
    }

    override func setBinders() {
        // Setup reactive bindings
        currentLocationRelay.asObservable()
            .subscribe(onNext: { [weak self] location in
                self?.updateDataStateWith { state in
                    state?.nextButtonIsEnable = location != nil
                    guard let location = location else { return }
                    state?.mapViewCameraPosition = location
                    state?.updateLocationInfo = location
                }
            })
            .disposed(by: disposeBag)
    }

    override func emitEvent(_ event: CICOLocationViewModelEvent) {
        switch event {
        case .viewDidLoad:
            handleViewDidLoad()
        case .submitButtonTapped:
            handleSubmit()
        case .reloadLocationTapped:
            handleReloadLocation()
        case .backButtonTapped:
            navigator?.back()
        case .openCameraForSelfie:
            emitAction(.openCamera)
        }
    }

    // MARK: - Private

    private func handleViewDidLoad() {
        updateDataState { state in
            state.appBarTitle = "Check In"
            state.submitButtonTitle = "Submit Attendance"
        }

        locationManager.startUpdatingLocation()
    }

    private func handleSubmit() {
        guard let location = currentLocationRelay.value else { return }

        emitAction(.showLoading)

        let payload = PostSubmitCICOUseCase.Params.Payload(
            employeeId: userViewModel.employeeId,
            scheduleId: scheduleData?.id.orZero(),
            latitude: location.coordinate.latitude,
            longitude: location.coordinate.longitude,
            media: selfieImage,
            notes: notes
        )

        let params = PostSubmitCICOUseCase.Params(
            companyId: userViewModel.companyId,
            payload: payload
        )

        postSubmitCICOUseCase.execute(params: params) { [weak self] result in
            self?.emitAction(.hideLoading)

            switch result {
            case .success(let model):
                self?.emitAction(.navigateToSuccess)
            case .failure(let error):
                self?.emitAction(.showToast(message: error.message.orEmpty()))
            }
        }
    }

    private func handleReloadLocation() {
        locationManager.requestLocation()
    }
}
```

**ViewModel Pattern Summary:**
- Inject dependencies via constructor with defaults
- Use UseCases for all data operations
- State updates via `updateDataState` or `updateDataStateWith`
- Emit actions to communicate with ViewController
- Use `weak self` in closures
- Dispose subscriptions via `disposeBag`

## ViewController <!-- 133 -->

```swift
// Presentation/View/CICOLocation/CICOLocationViewController.swift
class CICOLocationViewController: TalentaBaseViewController {

    // MARK: - UI
    private let mapView: GMSMapView = {
        let mapView = GMSMapView()
        return mapView
    }()

    private let submitButton: MPButton = {
        let button = MPButton()
        button.setTitle("Submit", for: .normal)
        return button
    }()

    // MARK: - ViewModel
    private let viewModel: CICOLocationViewModel

    // MARK: - Init
    init(viewModel: CICOLocationViewModel) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) not implemented")
    }

    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        bindViewModel()
        viewModel.emitEvent(.viewDidLoad)
    }

    // MARK: - Setup
    private func setupUI() {
        view.backgroundColor = .white
        view.addSubview(mapView)
        view.addSubview(submitButton)

        // Layout constraints...
        submitButton.addTarget(self, action: #selector(submitButtonTapped), for: .touchUpInside)
    }

    private func bindViewModel() {
        // Bind state changes
        viewModel.stateDriver
            .drive(onNext: { [weak self] state in
                self?.render(state: state)
            })
            .disposed(by: disposeBag)

        // Bind actions
        viewModel.actionDriver
            .drive(onNext: { [weak self] action in
                self?.handle(action: action)
            })
            .disposed(by: disposeBag)

        // Bind common actions
        viewModel.commonActionDriver
            .drive(onNext: { [weak self] action in
                self?.handleCommonAction(action: action)
            })
            .disposed(by: disposeBag)
    }

    private func render(state: CICOLocationViewModelState) {
        title = state.appBarTitle
        submitButton.setTitle(state.submitButtonTitle, for: .normal)
        submitButton.isEnabled = state.nextButtonIsEnable

        if let cameraPosition = state.mapViewCameraPosition {
            let camera = GMSCameraPosition.camera(
                withLatitude: cameraPosition.coordinate.latitude,
                longitude: cameraPosition.coordinate.longitude,
                zoom: 15
            )
            mapView.camera = camera
        }
    }

    private func handle(action: CICOLocationViewModelAction) {
        switch action {
        case .showToast(let message):
            showToast(message: message)
        case .showLoading:
            showLoading()
        case .hideLoading:
            hideLoading()
        case .openCamera:
            openCamera()
        case .navigateToSuccess:
            break // Coordinator handles
        case .navigationItemRightBarButtonItemRemoveAnimation:
            break
        }
    }

    private func handleCommonAction(_ action: CommonViewModelAction) {
        switch action {
        case .showToast(let message):
            showToast(message: message)
        case .showLoading:
            showLoading()
        case .hideLoading:
            hideLoading()
        }
    }

    // MARK: - Actions
    @objc private func submitButtonTapped() {
        viewModel.emitEvent(.submitButtonTapped)
    }
}
```

**ViewController Pattern:**
- Inject ViewModel via constructor
- Call `viewModel.emitEvent(.viewDidLoad)` in `viewDidLoad()`
- Bind `stateDriver` → render UI
- Bind `actionDriver` → handle actions
- UI events call `viewModel.emitEvent(...)`
- Pure UI logic stays in ViewController
- Business logic stays in ViewModel

---

## Advanced Patterns <!-- 2 -->

## Complex Dependency Management <!-- 58 -->

When ViewModels have 20+ dependencies, organize them systematically using MARK comments:

```swift
final class CICOLocationViewModel: BaseViewModelV2<CICOLocationViewModelState, CICOLocationViewModelEvent, CICOLocationViewModelAction> {

    // MARK: INJECTED
    private weak var navigator: (any CICOLocationNavigator)?

    // MARK: DEPENDENCIES
    private let getAttendanceLocationUseCase: any GetAttendanceLocationUseCaseProtocol
    private let getAttendancePolicyUseCase: any GetAttendancePolicyUseCaseProtocol
    private let checkCICOOutsidePolicyUseCase: any CheckCICOOutsidePolicyUseCaseProtocol
    private let getLiveAttendanceSettingUseCase: any GetLiveAttendanceSettingUseCaseProtocol
    private let getActiveScheduleUseCase: any GetActiveScheduleUseCaseProtocol
    // ... 15+ more use cases

    // MARK: UTILS
    private let mekariFlagCustomRepository: any MekariFlagCustomProtocol
    private let analytics: any TalentaAnalyticsProtocol
    private let dateFormatter: DateFormatter
    private let locationManager: CLLocationManager

    // MARK: DATA
    private var activeSchedule: ScheduleModel?
    private var liveAttendanceSetting: LiveAttendanceSettingModel?
    private var selectedSchedule: ScheduleModel?

    // MARK: STATE
    private let backEventSubject = PublishSubject<CICOLocationResult>()
    private let locationFraudEvent = BehaviorRelay<Bool>(value: true)
    private let updateLocationFraudSubject = PublishSubject<Void>()

    init(
        navigator: (any CICOLocationNavigator)? = nil,
        getAttendanceLocationUseCase: any GetAttendanceLocationUseCaseProtocol = GetAttendanceLocationUseCase.sharedInstance,
        getAttendancePolicyUseCase: any GetAttendancePolicyUseCaseProtocol = GetAttendancePolicyUseCase.sharedInstance,
        // ... all other dependencies with defaults
        mekariFlagCustomRepository: any MekariFlagCustomProtocol = MekariFlagCustomRepository.shared,
        analytics: any TalentaAnalyticsProtocol = TalentaAnalytics.shared,
        mainScheduler: SchedulerType = MainScheduler.instance
    ) {
        self.navigator = navigator
        self.getAttendanceLocationUseCase = getAttendanceLocationUseCase
        self.getAttendancePolicyUseCase = getAttendancePolicyUseCase
        // ... assign all dependencies
        super.init(mainScheduler: mainScheduler)
    }
}
```

**Key Principles:**
- **Group by category**: INJECTED (navigation), DEPENDENCIES (use cases), UTILS (shared tools), DATA (cached data), STATE (reactive streams)
- **Weak navigator**: Always use `weak` for navigator/coordinator references
- **Default singletons**: Every dependency has default parameter for testability
- **Protocol types**: Use `any ProtocolName` for all dependencies to enable mocking

## Navigator Protocol Pattern <!-- 39 -->

ViewModels never perform navigation directly. Use Navigator protocol with weak reference:

```swift
// Define Navigator protocol
protocol CICOLocationNavigator: AnyObject {
    func back(result: CICOLocationResult)
    func showLocationFraudSheet() -> Observable<Void>
    func showPolicySheet() -> Observable<Void>
}

// In ViewModel
final class CICOLocationViewModel {
    private weak var navigator: (any CICOLocationNavigator)?

    init(navigator: (any CICOLocationNavigator)? = nil) {
        self.navigator = navigator
        super.init()
    }

    private func handleBackButton() {
        let result = CICOLocationResult(location: selectedLocation)
        navigator?.back(result: result)
    }

    private func handleShowPolicyTapped() -> Observable<Action> {
        return (navigator?.showPolicySheet()).orEmpty()
            .map { _ in Action.policySheetClosed }
    }
}
```

**Key Points:**
- Navigator is a protocol, not a concrete class
- Always use `weak var` to prevent retain cycles
- Navigation methods can return `Observable<T>` for bidirectional data flow
- Use `.orEmpty()` when calling optional navigator methods that return Observable

## Coordinator Pattern <!-- 25 -->

```swift
protocol [Feature]Coordinator: AnyObject {
    func start()
    func navigateToDetail(_ item: ItemModel)
    func navigateBack()
    func showError(_ error: BaseErrorModel)
}

class [Feature]CoordinatorImpl: [Feature]Coordinator {
    private weak var navigationController: UINavigationController?

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func start() {
        let viewModel = [Feature]ViewModel()
        let viewController = [Feature]ViewController(viewModel: viewModel, coordinator: self)
        navigationController?.pushViewController(viewController, animated: true)
    }
}
```

## Advanced RxSwift Patterns <!-- 75 -->

### Observable.zip for Parallel Requests

When you need multiple API calls to complete before processing:

```swift
private func loadInitialData() -> Observable<Action> {
    return Observable.zip(
        getActiveScheduleUseCase.execute(param: nil),
        getLiveAttendanceSettingUseCase.execute(param: nil),
        getAttendancePolicyUseCase.execute(param: nil)
    )
    .map { [weak self] (schedules, liveSetting, policy) -> Action in
        guard let self = self else { return .empty }
        self.activeSchedule = schedules.first
        self.liveAttendanceSetting = liveSetting
        return .dataLoaded(schedule: schedules.first, policy: policy)
    }
    .catch { error in
        .just(.showError(error.toBaseError()))
    }
}
```

### Background Processing with Scheduler

For heavy computation, use background scheduler then switch back to main:

```swift
final class AttendanceScheduleViewModel {
    private let backgroundScheduler: SchedulerType = ConcurrentDispatchQueueScheduler(
        queue: DispatchQueue(label: "schedulescomponent.data.process", qos: .userInitiated)
    )
    private let mainScheduler: SchedulerType

    private func processSchedules(_ schedules: [ScheduleModel]) -> Observable<Action> {
        return Observable.just(schedules)
            .observe(on: backgroundScheduler)
            .compactMap { [weak self] schedules in
                guard let self = self else { return nil }
                return self.findDefaultShift(schedules: schedules)
            }
            .flatMap { $0 }
            .observe(on: mainScheduler)
            .map { index in Action.defaultShiftFound(index: index) }
    }
}
```

### Share with Replay for Multiple Subscribers

When multiple observers need the same expensive operation result:

```swift
private func loadAllData() -> Observable<Action> {
    let shared = Observable.zip(
        getActiveSchedulesUseCase.execute(param: nil),
        getAsyncProcessUseCase.execute(param: nil),
        getOnCallPlanningsUseCase.execute(param: nil)
    )
    .share(replay: 1, scope: .forever)

    shared.subscribe(onNext: { [weak self] result in
        self?.handleSchedules(result.0)
    }).disposed(by: disposeBag)

    shared.subscribe(onNext: { [weak self] result in
        self?.handlePlannings(result.2)
    }).disposed(by: disposeBag)

    return shared.map { _ in .dataLoaded }
}
```

## UIModel Pattern with copyWith <!-- 35 -->

ViewModels expose UIModels for the presentation layer, not domain entities:

```swift
struct ClockInConfirmationUIModel {
    let shiftName: String
    let shiftTime: String
    let isLiveTrackingEnabled: Bool
    let isLiveTrackingChecked: Bool
    let locationName: String

    func copyWith(
        shiftName: String? = nil,
        shiftTime: String? = nil,
        isLiveTrackingEnabled: Bool? = nil,
        isLiveTrackingChecked: Bool? = nil,
        locationName: String? = nil
    ) -> ClockInConfirmationUIModel {
        return ClockInConfirmationUIModel(
            shiftName: shiftName ?? self.shiftName,
            shiftTime: shiftTime ?? self.shiftTime,
            isLiveTrackingEnabled: isLiveTrackingEnabled ?? self.isLiveTrackingEnabled,
            isLiveTrackingChecked: isLiveTrackingChecked ?? self.isLiveTrackingChecked,
            locationName: locationName ?? self.locationName
        )
    }
}
```

**Key Benefits:**
- **Immutability**: UIModels are immutable, use `copyWith` for updates
- **Separation**: Keeps presentation logic out of domain entities
- **Type Safety**: Compiler ensures UI only receives formatted data

## Advanced State Management <!-- 32 -->

Beyond the single State pattern, use specialized relays for specific flows:

```swift
final class CICOBottomSheetViewModel {
    // Main State (BaseViewModelV2 pattern)
    struct State {
        var dataState: DataState<ClockInConfirmationUIModel> = .initial
    }

    // Specialized Relays
    private let locationFraudEvent = BehaviorRelay<Bool>(value: true)
    private let backEventSubject = PublishSubject<CICOLocationResult>()
    private let liveTrackingToggleRelay = BehaviorRelay<Bool>(value: false)

    var locationFraudDriver: Driver<Bool> {
        return locationFraudEvent.asDriver()
    }

    var backEventObservable: Observable<CICOLocationResult> {
        return backEventSubject.asObservable()
    }
}
```

**When to use what:**
- **State (DataState)**: Main UI state (loading, success, error)
- **BehaviorRelay**: Values that change over time, need current value
- **PublishSubject**: One-time events or commands (navigation, user actions)
- **Driver**: Safe UI binding (never errors, on main thread)

## Memory Management & deinit <!-- 17 -->

Always implement `deinit` to clean up resources:

```swift
deinit {
    print("deinit:: \(String(describing: Self.self))")
    locationManager.stopUpdatingLocation()
    locationManager.delegate = nil
    backEventSubject.onCompleted()
    timerDisposable?.dispose()
}
```

**What to clean up:** location managers, publish/behavior subjects (`.onCompleted()`), timers, file handles.
Always log `deinit` to catch retain cycles.

## Feature Flags Integration <!-- 26 -->

```swift
final class CICOLocationViewModel {
    private let mekariFlagCustomRepository: any MekariFlagCustomProtocol

    init(
        mekariFlagCustomRepository: any MekariFlagCustomProtocol = MekariFlagCustomRepository.shared
    ) {
        self.mekariFlagCustomRepository = mekariFlagCustomRepository
        super.init()
    }

    private func checkFeatureAvailability() -> Bool {
        return mekariFlagCustomRepository.getBoolValue(
            featureKey: "enable_live_tracking",
            defaultValue: false
        )
    }
}
```

**Best Practices:** Inject as protocol for testability. Always provide `defaultValue`. Check flags before expensive operations.

---

## Shared Component Paths <!-- 12 -->

When running a Component Reuse Check, search these locations for existing reusable views:

| Scope | Path | File pattern |
|---|---|---|
| Shared across all modules | `Talenta/Shared/Presentation/View/` | `*View.swift` |
| Shared shimmer/loading views | `Talenta/Shared/Presentation/ShimmerView/` | `*View.swift` |
| Shared table view components | `Talenta/Shared/Presentation/CustomTableView/` | `*View.swift` |
| Module-local views (cross-feature reuse candidate) | `Talenta/Module/*/Presentation/View/` | `*View.swift` |

**Search strategy:** Grep for the component concept (e.g. `"Card"`, `"Avatar"`, `"EmptyState"`, `"ListItem"`) across these paths before creating a new view. A `UIView` or `UIViewController` subclass found here is a reuse candidate.
