# Error Handling

Canonical, platform-agnostic principles for error handling across CLEAN Architecture layers.
Platform syntax and patterns: `reference/code-architecture/error-handling-impl.md` in each platform directory.

---

## Error Flow <!-- 20 -->

Errors travel inward-to-outward, mapped at each layer boundary:

```
DataSource throws transport error (NetworkError, HTTP 4xx/5xx, DB exception)
    ↓ caught and mapped by
Repository Implementation → DomainError
    ↓ returned to
Use Case → propagates DomainError unchanged
    ↓ received by
StateHolder → maps to UI error State
    ↓ observed by
Screen → renders error UI
```

**Rule:** Each layer catches the error type from the layer below it and converts it to the type its consumers expect. No raw transport errors escape the Data layer. No domain errors escape the Presentation layer uncaught.

---

## Error Types <!-- 12 -->

| Layer | Error type owned | Purpose |
|---|---|---|
| Data (transport) | Platform HTTP/network error | Represents wire failures — HTTP status, timeout, parse failure |
| Domain | `DomainError` | Business-meaningful error codes (`notFound`, `validationFailed`, `unauthorized`) |
| Presentation | UI error State | What the screen renders — message, retry action, recovery path |

**Domain error codes are business vocabulary** — `notFound`, `validationFailed`, `unauthorized`, `networkUnavailable`, `serverError`. Never use HTTP status codes as domain error codes.

---

## Error Mapping <!-- 15 -->

Repository implementations own the mapping from transport errors to domain errors:

- HTTP 404 → `DomainError.notFound`
- HTTP 401/403 → `DomainError.unauthorized`
- HTTP 422 / validation response → `DomainError.validationFailed`
- Network timeout / no connection → `DomainError.networkUnavailable`
- HTTP 5xx / unexpected → `DomainError.serverError`
- Parse failure → `DomainError.serverError` (malformed response is a server problem)

Mappers never throw — they handle null/missing fields defensively and return safe defaults.

---

## Error UI <!-- 14 -->

The StateHolder maps `DomainError` to an error State that the screen renders:

- **`notFound`** — show empty state with a descriptive message; offer navigation back
- **`validationFailed`** — show inline field errors; keep the form open for correction
- **`unauthorized`** — redirect to login or show a permission denied screen
- **`networkUnavailable`** — show offline banner with retry action
- **`serverError`** — show generic error with retry; log for observability

**Never show raw error messages or stack traces to users.** The StateHolder decides the user-facing copy; the Screen renders it.

---

## Layer Invariants <!-- 7 -->

- DataSources throw — they never return null to signal failure
- Repository implementations always catch and map — never let transport errors propagate to use cases
- Use cases propagate `DomainError` unchanged — they do not re-map errors
- StateHolders catch all errors from use cases — no unhandled promise rejections or uncaught exceptions reach the UI
- Screens never inspect error codes directly — they render the error State the StateHolder produces
