---
name: builder-pres-create-screen
description: |
  Create an MVP Presenter and Activity/Fragment pair implementing the feature Contract, using BaseMvpVbActivity and ErrorHandler.
user-invocable: false
---

Create a Presenter and Activity following `.claude/reference/code-architecture/presentation-impl.md ## Presenter section` and `## Activity / Fragment section`, and error handling in `.claude/reference/code-architecture/error-handling-impl.md ## ErrorHandler section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## Presenter` and `## Activity`; only **Read** the full file if the section cannot be located
2. **Grep** `.claude/reference/code-architecture/error-handling-impl.md` for `## ErrorHandler`
3. **Read** the Contract interface to understand all View and Presenter methods — never guess
4. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/presentation/[feature]/`
5. **Create** `[Feature]Presenter.kt` and `[Feature]Activity.kt` (or `[Feature]Fragment.kt`)
6. **Register** the activity in the DI module using `@ContributesAndroidInjector`

## Presenter Pattern

```kotlin
class FeaturePresenter @Inject constructor(
    private val getFeatureItemsUseCase: GetFeatureItemsUseCase,
    private val schedulerTransformers: SchedulerTransformers?,
    private val errorHandler: ErrorHandler
) : BasePresenter<FeatureContract.View>(), FeatureContract.Presenter {

    override fun loadFeatureItems(id: String) {
        val params = GetFeatureItemsUseCase.Params(id)
        getFeatureItemsUseCase.execute(params)
            .doOnSubscribe { view?.showLoading() }
            .doFinally { view?.hideLoading() }
            .subscribe(
                { items -> view?.showFeatureItems(items) },
                { error -> errorHandler.handle(error) { view?.showError(it) } }
            )
            .addToDisposables()
    }

    override fun refreshData() {
        loadFeatureItems(currentId)
    }
}
```

## Activity Pattern

```kotlin
class FeatureActivity :
    BaseMvpVbActivity<ActivityFeatureBinding, FeaturePresenter>(),
    FeatureContract.View {

    @Inject
    override lateinit var presenter: FeaturePresenter

    override val bindingInflater: (LayoutInflater) -> ActivityFeatureBinding
        get() = ActivityFeatureBinding::inflate

    override fun onViewCreated(savedInstanceState: Bundle?) {
        val featureId = intent.getStringExtra(EXTRA_FEATURE_ID).orEmpty()
        presenter.loadFeatureItems(featureId)

        binding.swipeRefresh.setOnRefreshListener { presenter.refreshData() }
    }

    override fun showFeatureItems(items: List<FeatureEntity>) { adapter.submitList(items) }
    override fun showError(error: Throwable) { showToast(error.message.orEmpty()) }
    override fun showEmptyState() { binding.emptyView.isVisible = true }

    companion object {
        private const val EXTRA_FEATURE_ID = "extra_feature_id"
        fun newIntent(context: Context, featureId: String) =
            Intent(context, FeatureActivity::class.java).apply {
                putExtra(EXTRA_FEATURE_ID, featureId)
            }
    }
}
```

Rules:
- `@Inject override lateinit var presenter` — Dagger field injection
- Extends `BaseMvpVbActivity<Binding, Presenter>` — handles `attachView`/`detachView` automatically
- `bindingInflater` property — no `setContentView` or `onCreate` override needed
- Override `onViewCreated` (not `onCreate`) for setup
- `doOnSubscribe`/`doFinally` for loading state — never manage showLoading/hideLoading manually in subscribe
- `errorHandler.handle(error) { view?.showError(it) }` — never `view?.showError(error.message.orEmpty())`
- `addToDisposables()` for cleanup — never `dispose()` manually
- `companion object { fun newIntent(...) }` for navigation

## Output

Confirm both file paths and list all Contract.View methods implemented and Contract.Presenter methods implemented.
