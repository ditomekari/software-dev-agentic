# Android — Presentation Layer (MVP)

> Concepts and invariants: `reference/code-architecture/presentation-theory.md`. This file covers Android MVP patterns with Kotlin.

## State Management <!-- 18 -->

Android MVP has no explicit state container. The **View interface** is the state surface — the Presenter drives it imperatively via `view?.show*` / `view?.hide*` calls. Loading, success, and error states are expressed as discrete View methods rather than a sealed state class.

```kotlin
interface TimeOffRequestContract {
    interface View : BaseMvpView {
        fun showLoading()        // loading state
        fun hideLoading()        // loading cleared
        fun showTimeOffRequests(requests: List<TimeOffRequest>)  // success state
        fun showError(error: Throwable)   // error state
        fun showEmptyState()              // empty state
    }
}
```

For screens that need richer state (e.g. multi-section loading), define a `ViewState` data class and expose it via a single `renderState(state: ViewState)` method on the View interface.

## Shared Component Paths <!-- 4 -->

> Android shared components are not yet catalogued. Add common widget paths here when established (e.g. `presentation/common/`, `base/ui/`).

## MVP Contract <!-- 28 -->

Interface defining the View and Presenter contracts for a feature screen.

```kotlin
// presentation/[feature]/TimeOffRequestContract.kt
interface TimeOffRequestContract {

    interface View : BaseMvpView {
        fun showTimeOffRequests(requests: List<TimeOffRequest>)
        fun showError(error: Throwable)
        fun showEmptyState()
    }

    interface Presenter : BaseMvpPresenter<View> {
        fun loadTimeOffRequests(id: String)
        fun refreshData()
    }
}
```

Rules:
- One Contract interface per screen
- `View` extends `BaseMvpView`; `Presenter` extends `BaseMvpPresenter<View>`
- View methods are UI commands: show/hide/navigate — no business logic
- Presenter methods correspond to user interactions and lifecycle events
- Name: `[Feature]Contract`

## Presenter <!-- 39 -->

Extends `BasePresenter<View>` — injects use case and `ErrorHandler` via Dagger.
Uses `doOnSubscribe`/`doFinally` for loading state, `addToDisposables()` for cleanup.

```kotlin
// presentation/[feature]/TimeOffRequestPresenter.kt
class TimeOffRequestPresenter @Inject constructor(
    private val getTimeOffRequestsUseCase: GetTimeOffRequestsUseCase,
    private val schedulerTransformers: SchedulerTransformers?,
    private val errorHandler: ErrorHandler
) : BasePresenter<TimeOffRequestContract.View>(), TimeOffRequestContract.Presenter {

    override fun loadTimeOffRequests(id: String) {
        val params = GetTimeOffRequestsUseCase.Params(id)
        getTimeOffRequestsUseCase.execute(params)
            .doOnSubscribe { view?.showLoading() }
            .doFinally { view?.hideLoading() }
            .subscribe(
                { requests -> view?.showTimeOffRequests(requests) },
                { error -> errorHandler.handle(error) { view?.showError(it) } }
            )
            .addToDisposables()
    }

    override fun refreshData() {
        // re-invoke loadTimeOffRequests
    }
}
```

Rules:
- `@Inject constructor` — Dagger provides use cases, SchedulerTransformers, ErrorHandler
- `doOnSubscribe { view?.showLoading() }` / `doFinally { view?.hideLoading() }` — loading state always managed this way
- `errorHandler.handle(error) { view?.showError(it) }` — never call `view?.showError(error.message.orEmpty())` directly
- `addToDisposables()` — disposes on `detachView()`; never call `dispose()` manually
- `view?.` guard on all view calls — view may be null after `detachView()`
- One presenter per screen

## Activity / Fragment <!-- 56 -->

Extends `BaseMvpVbActivity<Binding, Presenter>` — ViewBinding via `bindingInflater`, presenter injected via `@Inject`.

```kotlin
// presentation/[feature]/TimeOffRequestActivity.kt
class TimeOffRequestActivity :
    BaseMvpVbActivity<ActivityTimeOffRequestBinding, TimeOffRequestPresenter>(),
    TimeOffRequestContract.View {

    @Inject
    override lateinit var presenter: TimeOffRequestPresenter

    override val bindingInflater: (LayoutInflater) -> ActivityTimeOffRequestBinding
        get() = ActivityTimeOffRequestBinding::inflate

    override fun onViewCreated(savedInstanceState: Bundle?) {
        val featureId = intent.getStringExtra(EXTRA_FEATURE_ID)
        presenter.loadTimeOffRequests(featureId.orEmpty())

        binding.swipeRefresh.setOnRefreshListener {
            presenter.refreshData()
        }
    }

    override fun showTimeOffRequests(requests: List<TimeOffRequest>) {
        adapter.submitList(requests)
    }

    override fun showError(error: Throwable) {
        showToast(error.message.orEmpty())
    }

    override fun showEmptyState() {
        binding.emptyStateView.isVisible = true
    }

    companion object {
        private const val EXTRA_FEATURE_ID = "extra_feature_id"

        fun newIntent(context: Context, featureId: String) =
            Intent(context, TimeOffRequestActivity::class.java).apply {
                putExtra(EXTRA_FEATURE_ID, featureId)
            }
    }
}
```

Rules:
- Extends `BaseMvpVbActivity<Binding, Presenter>` — handles `attachView`/`detachView` lifecycle automatically
- `@Inject override lateinit var presenter` — Dagger field injection for presenter
- `bindingInflater` property provides the ViewBinding — no `setContentView` needed
- Override `onViewCreated` (not `onCreate`) for setup logic
- Use `companion object { fun newIntent(...) }` for activity launch — not direct `startActivity`
- `BaseMvpVbFragment` for Fragment-based screens — same pattern

## Navigation <!-- 36 -->

Custom `NavigationImpl` classes — not Android Navigation Component. Each feature defines an interface and implements it.

```kotlin
// navigation/TimeOffNavigation.kt (in base/common module)
interface TimeOffNavigation {
    fun navigateToTimeOffDetail(context: Context, requestId: String)
    fun navigateToSubmitTimeOff(context: Context)
}

// navigation/TimeOffNavigationImpl.kt
class TimeOffNavigationImpl @Inject constructor() : TimeOffNavigation {
    override fun navigateToTimeOffDetail(context: Context, requestId: String) {
        context.startActivity(TimeOffDetailActivity.newIntent(context, requestId))
    }

    override fun navigateToSubmitTimeOff(context: Context) {
        context.startActivity(SubmitTimeOffActivity.newIntent(context))
    }
}
```

Inject navigation into presenter when cross-screen navigation is needed:
```kotlin
class TimeOffPresenter @Inject constructor(
    private val useCase: GetTimeOffRequestsUseCase,
    private val navigation: TimeOffNavigation,
    private val errorHandler: ErrorHandler
) : BasePresenter<TimeOffContract.View>(), TimeOffContract.Presenter {

    override fun onRequestSelected(requestId: String) {
        view?.let { navigation.navigateToTimeOffDetail(it.getContext(), requestId) }
    }
}
```
