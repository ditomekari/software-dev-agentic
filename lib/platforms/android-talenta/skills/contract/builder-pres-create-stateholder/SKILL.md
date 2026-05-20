---
name: builder-pres-create-stateholder
description: |
  Create an MVP Contract interface defining View (BaseMvpView) and Presenter (BaseMvpPresenter) for a new feature screen.
user-invocable: false
---

> **Android mapping**: StateHolder = MVP Contract interface (`[Feature]Contract.kt`)

Create a Contract interface following `.claude/reference/code-architecture/presentation-impl.md ## MVP Contract section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## MVP Contract`; only **Read** the full file if the section cannot be located
2. **Read** the domain entity and use case to understand what the screen needs to display
3. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/presentation/[feature]/`
4. **Create** `[Feature]Contract.kt`

## Contract Pattern

```kotlin
interface FeatureContract {

    interface View : BaseMvpView {
        fun showFeatureItems(items: List<FeatureEntity>)
        fun showError(error: Throwable)
        fun showEmptyState()
    }

    interface Presenter : BaseMvpPresenter<View> {
        fun loadFeatureItems(id: String)
        fun refreshData()
    }
}
```

Rules:
- `View` extends `BaseMvpView` (not `BaseView`)
- `Presenter` extends `BaseMvpPresenter<View>` (not `BasePresenter`)
- View methods are UI commands: show/hide/navigate — no logic
- Presenter methods correspond to user interactions and lifecycle calls
- Name: `[Feature]Contract`

## Output

Confirm file path and list all View methods and Presenter methods declared. Then **write the stateholder contract file**:

```
.claude/agentic-state/runs/<feature>/stateholder-contract.md
```

Contract format:

```markdown
---
type: mvp-contract
contract_class: [Feature]Contract
file: feature_[module]/src/main/java/co/talenta/feature_[module]/presentation/[feature]/[Feature]Contract.kt
package: co.talenta.feature_[module].presentation.[feature]
---

## View Methods (implement in Fragment/Activity)
| Method | Parameters | When called by Presenter |
|---|---|---|
| showFeatureItems | items: List<[Feature]Entity> | on load success |
| showError | error: Throwable | on failure |
| showEmptyState | — | on empty result |

## Presenter Methods (call from Fragment/Activity)
| Method | Parameters | When to call |
|---|---|---|
| loadFeatureItems | id: String | in onViewCreated |
| refreshData | — | on swipe-to-refresh |

## Wiring Snippet
\```kotlin
// Fragment/Activity declares the contract
class [Feature]Fragment : BaseFragment(), [Feature]Contract.View {

    // inject or create presenter
    private lateinit var presenter: [Feature]Contract.Presenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        presenter.loadFeatureItems(id = args.id)
    }

    override fun showFeatureItems(items: List<[Feature]Entity>) { /* bind to RecyclerView */ }
    override fun showError(error: Throwable) { /* show error state */ }
    override fun showEmptyState() { /* show empty view */ }
}
\```
```

Fill every placeholder with real values from the Contract you just created. The wiring snippet must match actual View and Presenter method signatures.
