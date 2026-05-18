# Android — App Layer

> Concepts and invariants: `reference/code-architecture/app-layer-theory.md`. This file covers Kotlin/Dagger 2 patterns for Android.

## Dependency Registration <!-- 62 -->

Android uses **Dagger 2** with `@Module` + `@Binds` + `@ContributesAndroidInjector` per feature.

**Step 1 — Create the feature DI module:**

```kotlin
// feature_{feature}/di/Feature{Feature}Module.kt

@Module
abstract class Feature{Feature}Module {

    @Binds
    abstract fun bind{Feature}Repository(
        impl: {Feature}RepositoryImpl
    ): {Feature}Repository

    @Binds
    abstract fun bind{Feature}RemoteDataSource(
        impl: {Feature}RemoteDataSourceImpl
    ): {Feature}RemoteDataSource

    @ContributesAndroidInjector(modules = [Feature{Feature}Module::class])
    abstract fun contribute{Feature}Activity(): {Feature}Activity
}
```

**Step 2 — Create the ActivityBindingModule entry:**

```kotlin
// app/di/{Feature}ActivityBindingModule.kt

@Module
abstract class {Feature}ActivityBindingModule {

    @ContributesAndroidInjector(modules = [Feature{Feature}Module::class])
    abstract fun contribute{Feature}Activity(): {Feature}Activity
}
```

**Step 3 — Add to MainComponent:**

```kotlin
// app/di/MainComponent.kt
@Singleton
@Component(
    modules = [
        // ... existing modules
        {Feature}ActivityBindingModule::class,  // ← add here
    ]
)
interface MainComponent : AndroidInjector<App>
```

**Rules:**
- ✅ One `@Module` per feature under `feature_{feature}/di/`
- ✅ `@Binds` for interface-to-implementation binding — never `@Provides` for simple bindings
- ✅ `@ContributesAndroidInjector` scopes injection to the Activity/Fragment
- ❌ Never inject `Context` directly — use `@ApplicationContext` or `@ActivityContext`

---

## Route Registration <!-- 54 -->

Android uses **interface-based navigation** — the navigation interface lives in `base/`, the implementation lives in `app/navigator/`, and it is bound in a `NavigationModule`.

**Step 1 — Declare the navigation interface in `base/`:**

```kotlin
// base/navigation/{Feature}Navigation.kt

interface {Feature}Navigation {
    fun navigateTo{Feature}(context: Context)
    fun navigateTo{Feature}Detail(context: Context, id: String)
}
```

**Step 2 — Implement in `app/navigator/`:**

```kotlin
// app/navigator/{Feature}NavigationImpl.kt

class {Feature}NavigationImpl @Inject constructor() : {Feature}Navigation {

    override fun navigateTo{Feature}(context: Context) {
        context.startActivity(Intent(context, {Feature}Activity::class.java))
    }

    override fun navigateTo{Feature}Detail(context: Context, id: String) {
        context.startActivity(
            Intent(context, {Feature}DetailActivity::class.java).apply {
                putExtra({Feature}DetailActivity.EXTRA_ID, id)
            }
        )
    }
}
```

**Step 3 — Bind in NavigationModule:**

```kotlin
// app/di/NavigationModule.kt
@Module
abstract class NavigationModule {
    // ... existing bindings
    @Binds abstract fun bind{Feature}Navigation(impl: {Feature}NavigationImpl): {Feature}Navigation  // ← add here
}
```

**Rules:**
- ✅ Navigation interface in `base/` — never import Activity classes into feature modules
- ✅ One interface per feature, injected into ViewModels that need to navigate
- ❌ No `startActivity` calls inside feature module ViewModels — delegate to the navigator

---

## Module Registration <!-- 30 -->

Android module registration has two parts: wiring Dagger (via `MainComponent`) and wiring Gradle (via `settings.gradle`).

**Step 1 — Add to `settings.gradle`:**

```groovy
// settings.gradle
include ':feature_{feature}'   // ← add here
```

**Step 2 — Add to root `build.gradle` or `app/build.gradle` dependencies:**

```groovy
// app/build.gradle
dependencies {
    // ... existing
    implementation project(':feature_{feature}')   // ← add here
}
```

**Step 3 — Dagger wiring is handled in Dependency Registration (Step 3 above) — `{Feature}ActivityBindingModule` added to `MainComponent`.**

**Rules:**
- ✅ Module name in `settings.gradle` must match the directory name exactly
- ✅ Both Gradle wiring and Dagger wiring are required — neither alone is sufficient
- ❌ Never add feature module code directly to the `app/` module — keep feature code in `feature_{feature}/`

---

## Analytics Constants <!-- 15 -->

Analytics event names and screen identifiers are declared as constants in the feature module — never as inline strings in ViewModel or Fragment code.

**Path pattern:** `feature_{feature}/src/main/java/co/talenta/{feature}/analytics/{Feature}AnalyticsConstants.kt`

**Rules:**
- ✅ `object` with `const val String` constants — no logic, no analytics SDK import
- ✅ snake_case string values matching the analytics platform convention
- ❌ Never inline event name strings in ViewModel or Fragment

**When to create:** Any feature that instruments user interactions or screen views. Optional — skip if the feature has no analytics events.

---

## Feature Flag Registration <!-- 45 -->

Android has three flag types — pick the right enum based on the flag's backend:

| Type | Enum | Backend |
|---|---|---|
| Local only | `LocalFeatureFlag` | No backend — compile-time default |
| Firebase Remote Config | `RemoteConfigFeatureFlag` | `firebaseRemoteConfigKey` string |
| MekariFlag (Flagsmith) | `FlagsmithFeatureFlag` | `featureId` string |

All three implement the `Feature` interface (`domain/featureflag/Feature.kt`). Checked via `FeatureFlagManager.isFeatureEnabled(featureFlag)`.

**Add to the appropriate enum (`domain/featureflag/Feature.kt` or `flagsmith/FlagsmithFeatureFlag.kt`):**

```kotlin
// RemoteConfigFeatureFlag example
ENABLE_{FEATURE}(
    description = "Short description of what this gates",
    deprecated = arrayOf(),
    link = arrayOf("https://jurnal.atlassian.net/browse/{TICKET}"),
    defaultFlag = false,
    firebaseRemoteConfigKey = RemoteConfigKey.ENABLE_{FEATURE},
),

// FlagsmithFeatureFlag example
ENABLE_{FEATURE}(
    description = "Short description of what this gates",
    deprecated = arrayOf(),
    link = arrayOf("https://jurnal.atlassian.net/browse/{TICKET}"),
    defaultFlag = false,
    featureId = "enable_{feature}",
),
```

**Rules:**
- ✅ Always provide `description` and `link` — required for traceability
- ✅ `firebaseRemoteConfigKey` must match a constant in `RemoteConfigKey` — confirm with backend
- ✅ `featureId` must exactly match the Flagsmith feature key — confirm with backend
- ✅ `defaultFlag = false` unless the feature should be on by default when the flag is unreachable
- ❌ Never use raw string literals for flag keys at call sites — always reference the enum

**When to add:** Any feature that requires remote gating or gradual rollout. Optional — skip for features that launch to 100% of users immediately.

---

## Push Notification Registration <!-- 25 -->

Android centralizes FCM handling in `TalentaNotificationManagerImpl` (`app/src/main/java/co/talenta/service/fcm/TalentaNotificationManagerImpl.kt`). The FCM service in `AndroidManifest.xml` delegates to this class — no per-feature setup is needed.

**Token lifecycle:**
- `PostFcmTokenUseCase` — sends token to server (called in `HomeFragment.sendFcmTokenToServerIfNeeded()` after login)
- `DeleteFcmTokenUseCase` — deletes token from server on logout (called in `LogoutPresenter`, `ForgotPinLogoutPresenter`, `SessionExpiredActivity`)
- Last pushed token is stored in `SessionPreference.setLastPushedFcmToken(token)`

**Incoming message handling:**
- `TalentaNotificationManagerImpl.onMessageReceived()` receives the `RemoteMessage`
- Payload is in `remoteMessage.data["talenta_android_notification"]` — a JSON string deserialized into `TalentaNotificationPayload`
- `NotificationNavigationType` enum drives routing: `DEEPLINK`, `SCREEN_NAME`, `SILENT_PUSH_NOTIFICATION`, `URI`
- Silent push notifications route through domain use cases — they do not trigger UI state directly
- Display concerns (channels, icons, sound) are isolated in `TalentaNotificationBuilderImpl` — separate from the message handler

**Notification click routing:** notification pending intent targets `RedirectionActivity` — see Deeplink Registration below.

**Rules:**
- ✅ Per-feature notification types add a `NotificationNavigationType` variant and a handler in `TalentaNotificationManagerImpl`
- ✅ New notification screen destinations register a deeplink path and rely on `RedirectionActivity` for routing
- ❌ Never handle FCM messages or display notifications inside feature modules

---

## Deeplink Registration <!-- 53 -->

Android deeplinks enter through `RedirectionActivity` (`app/src/main/java/co/talenta/modul/redirection/RedirectionActivity.kt`) — a `singleTask` exported activity declared in `AndroidManifest.xml`.

**Two entry point types:**

| Type | Scheme | Handler |
|---|---|---|
| Custom scheme | `talenta://` (or `talenta.staging://`) | `checkTalentaDeepLink(uri)` |
| App link (universal) | `https://` / `http://` | `checkWebAppLink(uri)` |

**URL parsing:**
- `UrlHelper` (`base/src/main/java/co/talenta/base/helper/UrlHelper.kt`) — singleton with `contains()` pattern matching
- Each feature registers its URL pattern as a function: e.g., `isTaskDetail()` checks for `"task/detail"`
- Query parameters extracted via `uri.getQueryParameter(key)` — common keys: `id`, `action`, `date`, `type`

**Step 1 — Add a URL pattern to `UrlHelper`:**

```kotlin
// base/src/main/java/co/talenta/base/helper/UrlHelper.kt
fun Uri.is{Feature}(): Boolean = toString().contains("{feature-url-segment}")
```

**Step 2 — Add routing in `RedirectionActivity.checkTalentaDeepLink()`:**

```kotlin
uri.is{Feature}() -> redirect{Feature}(uri)
```

**Step 3 — Implement the redirect method:**

```kotlin
private fun redirect{Feature}(uri: Uri) {
    val id = uri.getQueryParameter("id").orEmpty()
    {feature}Navigation.navigateTo{Feature}(this, id)
}
```

**Step 4 — Register Intent filter for App Links (if universally linked):**

```xml
<!-- app/src/main/AndroidManifest.xml — inside RedirectionActivity intent-filter -->
<data android:pathPrefix="@string/universal_link_{feature}_index" />
```

**Rules:**
- ✅ All deeplink entry points flow through `RedirectionActivity` — never add `VIEW` intent filters to feature Activities
- ✅ URL patterns live in `UrlHelper` — never hardcode URL strings inside `RedirectionActivity`
- ✅ Routing delegates to the feature's Navigation interface — `RedirectionActivity` never starts Activities directly
- ❌ Never parse deeplink URLs in ViewModels or Fragments

---

## Planner Search Patterns <!-- 15 -->

Consumed by `builder-app-planner`. `{Feature}` = PascalCase, `{feature}` = snake_case per Android convention.

| Scope key | Glob / Path | Grep hint |
|---|---|---|
| `di` | `*Feature{Feature}Module.kt`, `*{Feature}ActivityBindingModule.kt`, `*MainComponent.kt` under `app/di/` | `{Feature}ActivityBindingModule` in `app/di/MainComponent.kt` |
| `route` | `*{Feature}Navigation.kt` under `base/navigation/`, `*{Feature}NavigationImpl.kt` under `app/navigator/`, `*NavigationModule.kt` under `app/di/` | `{Feature}Navigation` in `app/di/NavigationModule.kt` |
| `module` | `settings.gradle`, `app/build.gradle`, `*MainComponent.kt` under `app/di/` | `feature_{feature}` in `settings.gradle` |
| `analytics` | `*{Feature}AnalyticsConstants.kt` under `feature_{feature}/src/main/java/` | — |
| `feature_flag` | `domain/featureflag/Feature.kt`, `*FlagsmithFeatureFlag.kt` | `ENABLE_{FEATURE}` enum entry |
| `hybrid_embedding` | `bricks-talenta/*/module/*`, `app/*/brickhelper/*` | `## Hybrid Embedding` section below |

---

## Hybrid Embedding <!-- 138 -->

> Canonical terms and invariants: `reference/code-architecture/app-layer-theory.md` — `## Hybrid Embedding` section.
> This section covers Android-specific patterns using bricks-talenta + BrickHelper.

### Key Files <!-- 17 -->

| File | Role |
|------|------|
| `bricks-talenta/.../Bricks.kt` | Singleton entry point — engine init (`FlutterEngineGroup`), module factory, `preWarmEngine()` |
| `bricks-talenta/.../system/utils/BricksEngineManager.kt` | Engine lifecycle, MethodChannel wiring, `buildEngine()`, `listen()`, `invokeMethod()` |
| `bricks-talenta/.../system/models/BrickModule.kt` | Abstract base — declares `engine`, `host`, `open()`, `execute()`, `createExecutorEngineId()` |
| `bricks-talenta/.../system/activity/BrickActivity.kt` | `FlutterActivity` subclass — hosts the guest UI, wires `BrickChannelDelegate` in `configureFlutterEngine()` |
| `bricks-talenta/.../system/navigator/BrickChannelDelegate.kt` | Handles inbound MethodChannel calls from guest (`sendResponse`, `sendActionRequest`, `is24HourFormat`) |
| `bricks-talenta/.../system/navigator/BrickNavigator.kt` | Builds the `Intent` for `BrickActivity` and starts it |
| `bricks-talenta/.../system/executor/BrickExecutor.kt` | Headless execution — invokes guest and awaits typed `ExecutorCallback<T>` |
| `bricks-talenta/.../system/configs/BrickChannelConfig.kt` | Channel name and all method name / key constants |
| `app/.../helper/brickhelper/BrickHelper.kt` | HostParams Assembler — builds `hostParam` JSON, handles standard action callbacks (download, redirection, token update, locale change) |
| `bricks-talenta/.../module/talenta/TalentaModule.kt` | Concrete module — wraps all feature routes as typed `openXxx()` / `executeXxx()` methods |

### Host → Guest: Navigation Launch <!-- 31 -->

```kotlin
// 1. Obtain the module
val module = Bricks.getModule<TalentaModule>(context)

// 2. Build hostParam JSON via BrickHelper (HostParams Assembler)
val hostParamJson = BrickHelper.getDefaultJsonObject(
    sessionPreference, remoteConfigFlagProvider
).apply {
    put("moduleJson", JSONObject().apply { /* module-specific params */ }.toString())
}.toString()

val params = MainParams(hostParam = hostParamJson)   // LaunchParam on Android

// 3. Call the typed module API — BrickModule.open() → BrickNavigator → BrickActivity Intent
module.openPayslipIndex(
    context = context,
    params = params,
    launcher = activityResultLauncher,   // optional — to receive back-navigation result
    actionListener = brickActionListener // optional ActionListener for guest→host action callbacks
)
```

Under the hood:
- `TalentaModule.openPage()` calls `BricksEngineManager.buildEngine(context, engineId)` to create/reuse the `FlutterEngine`
- `BrickNavigator.launch()` starts `BrickActivity` with the encoded `brick://` URI as an Intent extra
- `BrickActivity.onCreate()` calls `BrickChannelDelegate.startChannel()` → `MethodChannel.invokeMethod("open", {uri: ...})`

### Host → Guest: Headless Execution <!-- 19 -->

```kotlin
module.executeTmClearDatabase(
    context = context,
    params = params,
    callBack = object : ExecutorCallback<TmClearDatabaseResponse> {
        override fun onLoading() { ... }
        override fun onSuccess(response: TmClearDatabaseResponse?) { ... }
        override fun onError(code: Int, message: String) { ... }
    }
)
```

- `createExecutorEngineId(baseEngineId)` creates a UUID-suffixed engine ID — isolated from the navigation engine to avoid lifecycle conflicts
- `BricksEngineManager.listen()` registers the `MethodChannel.setMethodCallHandler` before invoking — handles `sendResponse` reply from guest

### BrickHelper — HostParams Assembly <!-- 29 -->

`BrickHelper` is the HostParams Assembler on Android. `getDefaultJsonObject()` builds the standard JSON blob passed as `hostParam`:

```kotlin
JSONObject().apply {
    put("authenticationJson", JSONObject().apply {
        put("token", ...)
        put("refreshToken", ...)
        put("locale", ...)          // resolved via LocaleHelper
        put("isUseKong", ...)
        put("useLegacyEndpoint", ...)
    }.toString())
    put("userJson", getSafeJson(userResponse))    // URL-safe encoded user profile
    put("toggleJson", Gson().toJson(toggleResponse))
    put("featureFlagJson", Gson().toJson(featureFlagResponse))
}
```

Module-specific keys (e.g., `KEY_PAYSLIP_JSON`, `KEY_INBOX_JSON`) are appended before converting to `MainParams(hostParam = json.toString())`.

Device and app properties are passed as **top-level global config keys** (not inside `hostParam`):
- `BrickHelper.getFlutterAppProperty()` → `app_version`, `build_number`
- `BrickHelper.getFlutterDeviceProperty()` → `device_id`, `device_model`, `os_version`, `device_fingerprint`

These are not currently passed on iOS. If a guest feature reads these fields, coordinate with the iOS team to add them to `ModuleFactory`.

### Guest → Host: Action Callbacks (ActionListener) <!-- 18 -->

Android uses an explicit `BrickActionListener` interface (the ActionListener canonical term). `BrickHelper.getDefaultBrickActionListener()` provides a standard implementation covering:

| Action name constant | Effect |
|---------------------|--------|
| `ACTION_UPDATE_TOKEN` | Updates cached `MsiAuthData` in `SessionPreference` |
| `BRICK_CONSTANTS_ACTION_DOWNLOAD` | Downloads file via `FileDownloadManager` |
| `BRICK_CONSTANTS_ACTION_REDIRECTION` | Opens deeplink / internal / external URL |
| `BRICK_CONSTANTS_ACTION_EXIT_APPLICATION` | Calls `finishAffinity` + `exitProcess(0)` |
| `BRICK_CONSTANTS_ACTION_CHANGE_LOCALE` | Updates locale via `LocaleHelper` + `SessionPreference` |

Custom actions are handled via the `onListen` lambda parameter.

**iOS difference:** iOS has no separate `ActionListener` interface. The same action events are handled inline inside `BricksChannelDelegate.setupMethodHandler()`.

### Adding a New Module (Android) <!-- 11 -->

1. **Module class** — create `bricks-talenta/.../module/<name>/<Name>Module.kt` extending `BrickModule`; add typed `openXxx()` methods calling `openPage()`
2. **Config** — add `<Name>Config.kt` with `ENGINE_ID` (the engine cache slot key, must match `brick_constants.dart` on Flutter side) and `HOST` constants; add `<Name>Routes.kt` for route string constants
3. **Register in Bricks factory** — add a branch in both `Bricks.getModule<T>()` and `Bricks.preWarmEngine()` switch expressions
4. **ResponseHandler** — create `<Name>ResponseHandler.kt`; register in `BrickActivity.configureFlutterEngine()` by adding a branch to the `when (cachedEngineId?.split("@")?.first())` switch — `cachedEngineId` is the `ENGINE_ID` string from `<Name>Config.kt`
5. **HostParams** — define `<Name>Params` data class; add module-specific JSON keys as constants in `BrickHelper`
6. **Coordinate** `moduleHost` constant (`brick_constants.dart`) and `ENGINE_ID` with the guest (Flutter) team — these must match exactly

### MethodChannel Constants <!-- 14 -->

```kotlin
// BrickChannelConfig.kt
const val METHOD_CHANNEL           = "com.mekari.module"    // channel name
const val SEND_METHOD_OPEN         = "open"                  // host → guest: navigate
const val SEND_METHOD_EXECUTE      = "execute"               // host → guest: headless
const val RECEIVE_RESPONSE_METHOD  = "sendResponse"          // guest → host: result → ResponseHandler
const val RECEIVE_ACTION_METHOD    = "sendActionRequest"     // guest → host: action → BrickActionListener
const val IS_24_HOUR_FORMAT_METHOD = "is24HourFormat"        // guest → host: query (sync)
```

### Engine Lifecycle <!-- 8 -->

- `FlutterEngineGroup` is created once in `Bricks.initialize()` and held by `BricksEngineManager`
- Each module has a dedicated `ENGINE_ID` — engines are cached in `FlutterEngineCacheImpl`
- `BricksEngineManager.buildEngine(context, engineId)` reuses a cached engine or creates a new one via `FlutterEngine.dartExecutor.executeDartEntrypoint()` with config JSON as entrypoint args; `Bricks.preWarmEngine()` can be called at app start to create the engine before the user triggers navigation
- Navigation engine and executor engine use different IDs (`createExecutorEngineId` appends UUID) — prevents lifecycle conflict when both are active simultaneously
- `BricksEngineManager.destroyEngine(engineId)` is called in `BrickActivity.onDestroy()` and on lifecycle-observed destroy
- `BricksEngineManager.attachedEngineId` tracks the currently attached engine to guard against stale channel replies
