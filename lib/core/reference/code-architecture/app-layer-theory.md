# App Layer

Canonical, platform-agnostic definitions for App Layer wiring.
Platform syntax and patterns: `reference/code-architecture/app-layer-impl.md` in each platform directory.

---

## Dependency Registration <!-- 14 -->

**Dependency Registration** is the act of binding concrete implementations to their interfaces in the app's DI container so that the runtime can inject them into use cases, repositories, and state holders.

**Invariants:**
- Bindings live at the app shell — never inside a CLEAN layer
- Each feature owns its own registration unit (component, module, or file) — one file per feature
- Use cases and repositories are registered, not constructed inline at call sites
- Registration order follows the dependency graph: data sources → repositories → use cases

**When to add:** Any time a new use case, repository implementation, or data source is introduced. Skipping registration causes runtime crashes — this step is mandatory, not optional.

---

## Route Registration <!-- 14 -->

**Route Registration** is the act of declaring how the app navigates to a feature's screen — mapping a route identifier (string key, enum case, or coordinator type) to a screen factory.

**Invariants:**
- Routes live at the app shell or navigation coordinator — never inside a CLEAN layer
- Each feature owns one route declaration unit (route file, coordinator class, or destination enum)
- Route identifiers are stable string keys or typed values — not view instances
- Deep link destinations must be registered in the same place as regular routes

**When to add:** Any time a new screen is introduced. An unregistered route is a silent navigation failure.

---

## Module Registration <!-- 15 -->

**Module Registration** is the act of plugging a feature module into the app's module manager so it participates in the app lifecycle (startup, teardown, deep link handling).

**When it applies:** Only on platforms that have an explicit module system (`BaseModule`, `AppModule`, etc.). Platforms that use implicit linking (e.g. file-based routing) skip this step.

**Invariants:**
- Module registration happens in one place — the app's module manager or root coordinator
- Each feature module is registered once — duplicates cause double initialization
- Module lifecycle hooks (`onStart`, `onStop`) must not duplicate logic already in use cases

**When to add:** Any time a new feature module is introduced. Required only on platforms with an explicit `ModuleManager` or equivalent.

---

## Analytics Constants <!-- 13 -->

**Analytics Constants** are feature-scoped files that declare the event names, screen names, or tracking identifiers reported to the analytics service.

**Invariants:**
- One constants file per feature — never share event names across features in a single file
- Constants are plain string literals — no logic, no SDK imports
- Analytics SDK calls are made in the Presentation layer (ViewModel/BLoC) — these files only declare the identifiers they reference

**When to create:** Any feature that instruments user interactions or screen views. Optional — skip if the feature has no analytics events.

---

## Feature Flag Registration <!-- 13 -->

**Feature Flag Registration** is the act of declaring a new feature-gating key in the app's centralized flag registry, enabling remote enable/disable without a new app release.

**Invariants:**
- Flag keys live in a centralized registry (enum, struct, or constants file) — never as inline string literals at call sites
- One key per feature toggle — never reuse an existing flag for a different purpose
- Default values are explicit — the flag's behavior when unset must be defined in the registry

**When to add:** Any feature that requires remote gating, gradual rollout, or a kill switch. Optional — skip for features that launch immediately to 100% of users.

---

## Push Notification Registration <!-- 15 -->

**Push Notification Registration** is the act of wiring the app to receive push notifications — fetching the device token, delivering it to the server, and removing it on logout.

**Invariants:**
- Registration is owned by the infrastructure layer — never by an individual feature
- The notification manager is wired once at the app shell, not inside feature modules
- Payload routing (which screen or flow a notification opens) is declared separately from payload receipt (receiving and decoding the notification)
- Notification display concerns — channels, builders, and visual configuration — are isolated from the message handler
- Silent push notifications must route through domain use cases — they must not trigger UI state directly

**When to add:** Once per app. The token lifecycle is tied to the auth flow — token registration occurs on login and token deletion occurs on logout.

---

## Deeplink Registration <!-- 15 -->

**Deeplink Registration** is the act of mapping incoming URLs and notification taps to screens or flows within the app.

**Invariants:**
- Mappings live at the app shell — never inside individual feature modules
- Deeplink route identifiers are the same identifiers used for in-app navigation — no parallel routing system
- URL parsing is separated from routing — the parser produces a route identifier, the router acts on it
- Each feature declares its own deeplink paths; the app shell assembles the complete registry
- Deeplinks arriving while the app is backgrounded or unauthenticated must be queued and replayed after auth completes

**When to add:** Any feature reachable from a push notification tap, an external URL, or a cross-app link.

---

## Hybrid Embedding <!-- 83 -->

**Hybrid Embedding** is the architecture where a native host app (iOS or Android) embeds a Flutter module as a full-screen view or headless executor, communicating over MethodChannel via the Bridge library (`BrickWrap` / `brick_way`).

**When it applies:** iOS and Android hosts only. Not applicable to web or to Flutter apps that are the host.

**Invariants:**
- Module launch always goes through the Bridge (`BrickWrap` / `brick_way`) — never via raw `FlutterEngine` or `MethodChannel` directly
- Module registration, engine slot config, and HostParams assembly live in the host app shell — not inside individual feature screens
- Each module has exactly one engine slot ID — reusing an existing slot causes lifecycle conflicts
- The `brick://` URI scheme and engine slot ID must be agreed between host and guest teams before implementation begins

**When to add:** Any time a native feature needs to launch a Flutter screen, or a Flutter module needs to call back to native.

### Canonical Terms

| Term | Definition |
|------|-----------|
| **Host** | The native app (iOS or Android) that owns the process, lifecycle, and authentication state |
| **Guest** | The Flutter module embedded inside the host — a self-contained Dart runtime serving one or more feature routes |
| **Bridge** | The library layer (`BrickWrap` on host side, `brick_way` on guest side) that abstracts FlutterEngine management and MethodChannel wiring |
| **MethodChannel** | The Flutter SDK primitive used for bidirectional host↔guest communication over a named channel (`com.mekari.module`) |
| **Module** | A discrete guest feature unit registered by name (e.g., `TalentaModule`, `PayslipModule`). One module maps to one FlutterEngine cache slot |
| **Engine** | A `FlutterEngine` / `FlutterEngineGroup` instance that executes Dart code. Managed by `BricksEngineManager` on both iOS and Android host sides |
| **URI** | The routing primitive passed from host to guest: `brick://<module-host>/<route>?hostParam=<json>` |
| **HostParams** | JSON-serialized context injected by the host at launch time. Standard blobs: `authenticationJson` (token, refreshToken, locale, env flags), `userJson`, `toggleJson`, `featureFlagJson`. Android also passes `app_version`, `build_number`, `device_id`, `device_model`, `os_version`, `device_fingerprint` as top-level config keys |
| **HostParams Assembler** | Host-side component that builds the HostParams JSON blob before module launch. iOS: `ModuleFactory<T>` (`ModuleFactory.generateStringHostParams()`). Android: `BrickHelper.getDefaultJsonObject()` |
| **LaunchParam** | The value object passed to `openModule()` / `openPage()` carrying `BrickAddress` + HostParams. iOS type: `LaunchParams`. Android type: `MainParams(hostParam:)` |
| **Navigator** | Host-side component that launches a guest module as a full-screen view. iOS: `BricksNavigator` → `BricksViewController`. Android: `BrickNavigator` → `BrickActivity` (Intent) |
| **Executor** | Host-side component that invokes a guest module headlessly (no UI) and awaits a typed response. Uses a UUID-suffixed engine ID to isolate its lifecycle from the Navigator engine |
| **ResponseHandler** | Host-side per-module object that interprets the `sendResponse` MethodChannel payload and routes the result to the calling feature code. iOS: registered in `BricksViewController.getResponseHandler()`. Android: registered in `BrickActivity.configureFlutterEngine()` |
| **ActionListener** | Host-side callback handler for `sendActionRequest` events from the guest. Android: explicit `BrickActionListener` interface registered per `openPage()` call, with `BrickHelper.getDefaultBrickActionListener()` providing standard actions. iOS: handled inline inside `BricksChannelDelegate` — no separate listener object |
| **Router** | Guest-side component (`BrickRouter`) that resolves a URI to a `BrickWidget` |
| **BrickExecutor** | Guest-side component that processes a URI without rendering UI and returns an `ExecutorResponse` |

### Communication Directions

**Host → Guest (navigation launch)**

1. Host obtains a module via `Bricks.getModule(XModule)` — Bridge creates Navigator + Executor
2. Host calls `module.openModule(launchParam:)` / `module.openXxx()` — Bridge builds/reuses a FlutterEngine for the module's engine slot
3. Bridge serialises HostParams into JSON passed as Dart **entrypoint args** at engine creation time, AND encodes them as the `hostParam` query argument in the `brick://` URI — the guest reads them from the URI; the entrypoint args ensure they are available if the engine is pre-warmed before navigation
4. Bridge sends the `brick://` URI via `MethodChannel.invokeMethod("open", {uri: ...})`
5. Guest `BrickRouter.getTarget(uri:)` resolves the URI to a `BrickWidget` and renders it

**Host → Guest (headless execution)**

Same engine lifecycle, but uses `MethodChannel.invokeMethod("execute", {uri:, invocationId:})`.
Guest `BrickExecutor.execute(uri:)` processes the request and calls back with `MethodChannel.invokeMethod("sendResponse", {data:, invocationId:})`.
The executor engine uses a UUID-suffixed engine ID to avoid lifecycle conflict with a simultaneously active navigator engine.

**Guest → Host (response / action)**

| Method | Direction | Purpose |
|--------|-----------|---------|
| `sendResponse` | Guest → Host | Return data or error after navigation or execution; routed by `ResponseHandler` |
| `sendActionRequest` | Guest → Host | Request a host action (open native page, download, token refresh, etc.); routed by `ActionListener` |
| `is24HourFormat` | Guest → Host | Query device locale format — synchronous reply from the host |

**ActionListener asymmetry:** Android registers an explicit `BrickActionListener` per `openPage()` call. iOS handles the same events inline inside `BricksChannelDelegate` — there is no separate listener interface on iOS.

### Module Registration Pattern

Adding a new guest module requires coordinated changes on both sides:

**Host side:**
1. Add the module class under `BrickWrap/Modules/<Name>/` (iOS) or `bricks-talenta/.../module/<name>/` (Android)
2. Register the module in `Bricks.getModule()` switch; also register in `Bricks.preWarmEngine()` (Android only)
3. Create the engine slot constant (`engineId` / `ENGINE_ID`) in the module's config file
4. Create a `ResponseHandler` for the module and register it in the channel delegate switch (`BricksViewController.getResponseHandler()` on iOS, `BrickActivity.configureFlutterEngine()` on Android)
5. Add the HostParams assembler entry (`ModuleFactory.generateStringHostParams()` on iOS, `BrickHelper` module-specific keys on Android)

**Guest side:**
1. Implement `BrickModule` — declare `host`, `routes`, `executor`, `router`
2. Register the module's base route in the module manager's route resolver (the method that maps a base route string to a module handler)
3. Wire module-scoped DI bindings into the guest DI container and add to the module manager's initialization method
4. Call `ExternalDataSourceHelper.initializeConfig()` (or platform equivalent) in both `BrickRouter` and `BrickExecutor` to seed HostParams into in-memory config before rendering

**Cross-team (required):**
5. Agree on the `brick://` URI scheme (`moduleHost` constant in `brick_constants.dart`) and engine slot ID string between host and guest teams — these must match exactly

Platform-specific implementation patterns: platform `reference/code-architecture/hybrid-embedding-impl.md`.

