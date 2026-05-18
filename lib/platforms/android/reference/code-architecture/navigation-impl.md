# Android — Navigation

> Canonical terms and invariants: `reference/code-architecture/ui-theory.md` — `## Navigator / Coordinator` section.
> Android does not use the Navigation Component. Navigation is handled via custom `NavigationImpl` classes injected into presenters.

## Navigator <!-- 29 -->

Each feature defines a navigation interface and implementation. The presenter holds the interface; the Activity/Fragment provides the `Context`.

```kotlin
// navigation/TimeOffNavigation.kt (base/common module)
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

Rules:
- Navigation interfaces live in `base/common` module — not in feature modules
- Inject `Navigation` interface into Presenter, not Activity
- Activity provides `Context` via `view?.getContext()` — never store Activity reference in Presenter
- Each Activity exposes a `companion object { fun newIntent(...) }` factory

## Route Constants <!-- 3 -->

> Android does not use string route constants. Activity class references serve as the routing mechanism. If deep links are added, register URI patterns here.
