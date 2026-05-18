# iOS — Navigation

> Canonical terms and invariants: `reference/code-architecture/ui-theory.md` — `## Navigator / Coordinator` section.

Talenta uses the **Coordinator pattern** with `BaseCoordinator` to handle navigation and decouple ViewControllers from navigation logic.

## Navigator Protocol <!-- 26 -->

Define navigation methods as a protocol that the coordinator implements:

```swift
// Presentation/Coordinator/DashboardNavigator.swift
protocol DashboardNavigator: AnyObject {
    // Simple navigation (no result)
    func openTimeOff()
    func openPayslip()

    // Navigation with return value (Observable)
    func openLiveAttendance(isShowCSAT: Bool) -> Observable<LiveAttendanceResult>
    func showAllReimbursement() -> Observable<ReimbursementBottomSheetResult>

    // Navigation with parameters
    func openReimbursementIndex(requestReimbursementId: Int?)
    func showAnnouncementDetails(id: Int)
}
```

**Navigator Rules:**
- Methods that need results return `Observable<Result>`
- Methods with simple navigation return `Void`
- All methods take necessary parameters (IDs, flags, models)

## BaseCoordinator Pattern (V2 Recommended) <!-- 43 -->

```swift
// Presentation/Coordinator/DashboardCoordinator.swift
final class DashboardCoordinator: BaseCoordinator<Void> {

    // MARK: - Dependencies (injected via init)
    private let expenseManagementManager: ExpenseManagementProtocol
    private let timeManagementManager: TimeManagementManagerProtocol
    private weak var tabBarDelegate: MainTabDelegate?

    // MARK: - DI Container (V2)
    private let container = TalentaDashboardDIContainer.shared

    // MARK: - Initialization
    init(
        navigationController: UINavigationController?,
        expenseManagementManager: ExpenseManagementProtocol = ExpenseManagementManager(),
        timeManagementManager: TimeManagementManagerProtocol = TimeManagementManager(),
        tabBarDelegate: MainTabDelegate? = nil
    ) {
        self.expenseManagementManager = expenseManagementManager
        self.timeManagementManager = timeManagementManager

        super.init()

        self.defaultNavigationController = navigationController
        self.tabBarDelegate = tabBarDelegate
    }

    // MARK: - CreateController (Required by BaseCoordinator)
    override func createController() -> UIViewController {
        // V2: Use DI Container factory method
        let viewModel = container.makeDashboardViewModel(navigator: self)

        let viewController = DashboardViewController(viewModel: viewModel)
        self.defaultController = viewController

        return viewController
    }
}
```

## Navigator Implementation <!-- 69 -->

```swift
extension DashboardCoordinator: DashboardNavigator {

    // Simple navigation (no result)
    func openTimeOff() {
        FirebaseAnalyticsHelper.sharedInstance.logEvent(eventName: AnalyticsEvent.timeOffHome.eventName)

        guard let navVc = self.defaultNavigationController else { return }
        self.timeManagementManager.setPresentedViewController(navVc)
        self.timeManagementManager.openTmTimeOffIndex()
            .subscribe()
            .disposed(by: disposeBag)
    }

    // Navigation with child coordinator (no result)
    func openTask() {
        FirebaseAnalyticsHelper.sharedInstance.logEvent(eventName: AnalyticsEvent.taskViewAllHome.eventName)

        let coordinator = TaskIndexCoordinator(navigationController: self.defaultNavigationController, isSearchMode: false)

        self.coordinate(to: coordinator)
            .subscribe()
            .disposed(by: disposeBag)
    }

    // Navigation with result (Observable)
    func openLiveAttendance(isShowCSAT: Bool) -> Observable<LiveAttendanceResult> {
        let coordinator = LiveAttendanceCoordinator(
            navigationController: self.defaultNavigationController,
            isFromWidget: false,
            isShowCSAT: isShowCSAT
        )

        return self.coordinate(to: coordinator)
    }

    // Bottom sheet presentation with result
    func showAllReimbursement() -> Observable<ReimbursementBottomSheetResult> {
        let coordinator = ReimbursementBottomSheetCoordinator(navigationController: self.defaultNavigationController)
        return self.coordinate(to: coordinator)
    }

    // Bottom sheet with custom view
    func showAllAppsBottomSheet(menuItems: [MenuItemUIModel]) -> Observable<String> {
        let model = AllAppsBottomSheetUIModel(
            title: R.string.talentaNativeLocalizations.all_apps.localized(),
            menuItems: menuItems
        )

        let allAppsView = AllAppsBottomSheetView()
        allAppsView.configure(with: model)

        // BaseCoordinator's presentBottomSheet helper
        return presentBottomSheet(
            view: allAppsView,
            title: model.title,
            rightActionTitle: .closeIcon,
            backgroundAlpha: 0.2,
            headerBgColor: MPColor.gray25,
            interactionDriver: allAppsView.menuItemTapDriver,
            shouldDismiss: { _ in true },
            shouldAnimate: { _ in false }
        )
    }
}
```

## Coordinator Lifecycle Management <!-- 34 -->

**Child Coordinator Pattern:**

```swift
// Start child coordinator with result
func openSomeFeature() -> Observable<FeatureResult> {
    let coordinator = FeatureCoordinator(navigationController: self.defaultNavigationController)

    // coordinate(to:) automatically:
    // 1. Adds child to childCoordinators array
    // 2. Calls coordinator.start()
    // 3. Returns Observable<Result>
    // 4. Removes child when Observable completes
    return self.coordinate(to: coordinator)
}

// Start child coordinator without result
func openAnotherFeature() {
    let coordinator = AnotherFeatureCoordinator(navigationController: self.defaultNavigationController)

    self.coordinate(to: coordinator)
        .subscribe()
        .disposed(by: disposeBag)
}
```

**BaseCoordinator provides:**
- `coordinate(to: Coordinator<T>) -> Observable<T>` - Manages child lifecycle
- `presentBottomSheet(...)` - Reusable bottom sheet presentation
- `disposeBag` - Automatic subscription management
- `defaultNavigationController` - Shared navigation controller
- `defaultController` - Reference to created view controller

## V2 Pattern with DI Container <!-- 32 -->

**In Coordinator:**
```swift
override func createController() -> UIViewController {
    // V2: Use DI Container factory
    let viewModel = TalentaDashboardDIContainer.shared.makeDashboardViewModel(navigator: self)

    let viewController = DashboardViewController(viewModel: viewModel)
    self.defaultController = viewController

    return viewController
}
```

**In DI Container:**
```swift
// TalentaDashboard/DI/TalentaDashboardDIContainer.swift
final class TalentaDashboardDIContainer {
    static let shared = TalentaDashboardDIContainer()

    // ViewModel factory
    func makeDashboardViewModel(navigator: DashboardNavigator) -> DashboardViewModel {
        DashboardViewModel(
            navigator: navigator,
            getDashboardDataUseCase: getDashboardDataUseCase,
            analyticsService: SharedDIContainer.shared.analyticsService
        )
    }
}
```

## Coordinator Patterns Summary <!-- 10 -->

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Simple push** | Direct ViewController push | `navigationController?.pushViewController(vc, animated: true)` |
| **Child coordinator (no result)** | Feature with own navigation flow | `coordinate(to: TaskIndexCoordinator()).subscribe()` |
| **Child coordinator (with result)** | Need callback from child | `coordinate(to: LiveAttendanceCoordinator()) -> Observable<Result>` |
| **Bottom sheet** | Modal presentation with custom view | `presentBottomSheet(view: customView, ...)` |
| **Feature module manager** | Cross-module navigation | `timeManagementManager.openTmTimeOffIndex()` |

## Complete Example: Feature Coordinator <!-- 74 -->

```swift
// Presentation/Coordinator/CustomFormListCoordinator.swift

// 1. Navigator Protocol
protocol CustomFormListNavigator: AnyObject {
    func openFormDetail(formId: Int)
    func openCreateForm() -> Observable<CustomFormCreationResult>
    func showDeleteConfirmation(formId: Int) -> Observable<Bool>
}

// 2. Coordinator Implementation
final class CustomFormListCoordinator: BaseCoordinator<Void> {

    private let container = FeatureIntegrationDIContainer.shared

    init(navigationController: UINavigationController?) {
        super.init()
        self.defaultNavigationController = navigationController
    }

    override func createController() -> UIViewController {
        // V2: DI Container creates ViewModel
        let viewModel = container.makeCustomFormListViewModel(navigator: self)
        let viewController = CustomFormListViewController(viewModel: viewModel)
        self.defaultController = viewController

        return viewController
    }
}

// 3. Navigator Implementation
extension CustomFormListCoordinator: CustomFormListNavigator {

    func openFormDetail(formId: Int) {
        let coordinator = CustomFormDetailCoordinator(
            navigationController: self.defaultNavigationController,
            formId: formId
        )

        self.coordinate(to: coordinator)
            .subscribe()
            .disposed(by: disposeBag)
    }

    func openCreateForm() -> Observable<CustomFormCreationResult> {
        let coordinator = CustomFormCreateCoordinator(navigationController: self.defaultNavigationController)
        return self.coordinate(to: coordinator)
    }

    func showDeleteConfirmation(formId: Int) -> Observable<Bool> {
        let alertView = DeleteConfirmationView(formId: formId)

        return presentBottomSheet(
            view: alertView,
            title: R.string.talentaNativeLocalizations.delete_form.localized(),
            rightActionTitle: .closeIcon,
            interactionDriver: alertView.confirmTapDriver,
            shouldDismiss: { _ in true },
            shouldAnimate: { _ in true }
        )
    }
}
```

**Coordinator Pattern Rules:**
- Inherit from `BaseCoordinator<ResultType>` (V2 standard)
- Define `Navigator` protocol for all navigation methods
- Implement protocol in extension
- Use DI Container factory methods for ViewModel creation
- Use `coordinate(to:)` for child coordinator management
- Use `presentBottomSheet()` for modal presentations
- Dispose subscriptions with `disposeBag`
