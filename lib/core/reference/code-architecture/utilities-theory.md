# Core Services & Utilities

Canonical, platform-agnostic definitions for shared infrastructure services used across all Clean Architecture layers.
Platform syntax and implementations: `reference/code-architecture/utilities-impl.md` in each platform directory.

---

## StorageService <!-- 14 -->

**StorageService** is an interface-based key-value store for persisting tokens, user preferences, and cached data across app sessions.

**Invariants:**
- The interface lives in the infrastructure layer — never in domain or data
- All keys are typed constants (enum or sealed class) — never raw strings at call sites
- Implementations are swappable per environment (e.g. in-memory for tests, secure storage for production)
- `clearAll()` is only called on logout — never on individual feature teardown

**When to use:** Any layer that needs to read or write persistent state. Inject the interface — never access the concrete implementation directly.

---

## DateService <!-- 13 -->

**DateService** is a centralized abstraction for all date and time operations — formatting, parsing, comparison, and timezone handling.

**Invariants:**
- All date formatting and parsing goes through `DateService` — never via inline format strings or `SimpleDateFormat`/`DateFormatter` at call sites
- Timezone handling is explicit — never assume device timezone in business logic
- The interface is injectable for testing — implementations can return fixed dates in tests

**When to use:** Any layer that formats, parses, or compares dates. Domain layer may define date-related value objects; `DateService` handles the conversion to/from display and wire formats.

---

## Logger <!-- 14 -->

**Logger** is the centralized logging abstraction with severity levels. All log output goes through this interface.

**Invariants:**
- Severity levels: `debug`, `info`, `warning`, `error` — each with distinct routing (debug stripped in production)
- No `print` / `console.log` / `Log.d` calls at call sites — always use the Logger interface
- Sensitive data (tokens, PII) must never appear in log output
- The implementation routes to Crashlytics or the platform crash reporter for `error`-level events

**When to use:** Any layer that needs diagnostic output. Inject `Logger` — never call the platform logging API directly.

---

## Helper Extensions <!-- 11 -->

**Helper Extensions** are stateless utility functions scoped to a specific type — they extend built-in types with domain-safe convenience without introducing service dependencies.

**Invariants:**
- Extensions contain no business logic and no side effects — pure transformations only
- No analytics SDK, storage, or network imports inside extension files
- Grouped by the type they extend (e.g. `String+Formatting`, `Date+Helpers`) — never a catch-all utilities file
- Platform implementations live in `reference/code-architecture/utilities-impl.md` per platform

**When to use:** Repetitive type-level transformations that would otherwise be inlined everywhere. If the transformation requires injected state, it belongs in a use case or service, not an extension.
