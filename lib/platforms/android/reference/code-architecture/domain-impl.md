# Android — Domain Layer

> Concepts and invariants: `reference/code-architecture/domain-theory.md`. This file covers Kotlin syntax and Android-specific patterns.

## Dependency Rule <!-- 15 -->

Domain is the innermost layer — it imports nothing from outer layers.

**Allowed:** Kotlin standard library (`kotlin.*`), `java.io.Serializable`, `RxJava3` schedulers used only in the base `UseCase` infrastructure.

**Forbidden:**
- `import retrofit2.*` — networking belongs in data
- `import androidx.*` — any AndroidX import signals a framework dependency
- Room annotations (`@Entity`, `@ColumnInfo`) — database concerns belong in data
- OkHttp types — HTTP client belongs in data
- Any `*Response`, `*Api`, or `*RepositoryImpl` type from the data layer

---

## Entities <!-- 23 -->

Pure Kotlin data classes — no JSON annotations, no Android framework imports.

```kotlin
// domain/entity/TimeOffRequest.kt
data class TimeOffRequest(
    val id: String,
    val employeeId: String,
    val startDate: String,
    val endDate: String,
    val reason: String,
    val status: String,
    val totalDays: Int
)
```

Rules:
- Pure Kotlin data class — no `@SerializedName`, no `@Json`, no Android imports
- All properties non-optional at the domain boundary (use sensible defaults in mapper)
- Field names use domain terminology, not API field names
- Immutable — use `val` for all properties

## Repository Interfaces <!-- 18 -->

Defined in `domain/repository/` — platform-agnostic contracts only.

```kotlin
// domain/repository/TimeOffRepository.kt
interface TimeOffRepository {
    fun getTimeOffRequests(page: Int, limit: Int): Single<List<TimeOffRequest>>
    fun submitTimeOffRequest(request: SubmitTimeOffRequest): Single<TimeOffRequest>
}
```

Rules:
- Interface only — no implementation in domain layer
- Return `Single<T>` (RxJava 3) for all async operations
- Params are domain types — never response/DTO types
- Name: `[Module]Repository` (one interface per feature module)

## Use Cases <!-- 35 -->

Extend `SingleUseCase<Result, Params>` from `domain/usecase/base/`.

```kotlin
// domain/usecase/GetTimeOffRequestsUseCase.kt
@OpenForTesting
class GetTimeOffRequestsUseCase @Inject constructor(
    private val timeOffRepository: TimeOffRepository,
    schedulerTransformer: SchedulerTransformers? = null,
    logger: Logger? = null
) : SingleUseCase<List<TimeOffRequest>, GetTimeOffRequestsUseCase.Params>(
    schedulerTransformer?.applySingleIoSchedulers(),
    logger
) {

    override fun build(params: Params?): Single<List<TimeOffRequest>> = params!!.run {
        timeOffRepository.getTimeOffRequests(page, limit)
    }

    data class Params(
        val page: Int,
        val limit: Int
    )
}
```

Rules:
- Annotate with `@OpenForTesting` to allow mocking in tests
- Use `@Inject constructor` — never instantiate directly
- Inject `SchedulerTransformers` and `Logger` with nullable defaults (test-friendly)
- `Params` is a nested data class inside the use case
- Return type wraps the domain entity — never raw response types
- Name: `[Action][Entity]UseCase` (e.g. `GetTimeOffRequestsUseCase`, `SubmitTimeOffUseCase`)

## Domain Services <!-- 18 -->

Domain services encapsulate business logic that spans multiple entities or does not naturally belong to a single use case. In Android MVP, these are plain Kotlin classes with no Android framework dependencies.

```kotlin
// domain/service/TimeOffEligibilityService.kt
class TimeOffEligibilityService @Inject constructor() {
    fun isEligible(employee: Employee, requestDays: Int): Boolean {
        return employee.remainingLeave >= requestDays && !employee.isProbation
    }
}
```

Rules:
- Pure Kotlin — no Android imports, no RxJava, no framework dependencies
- Injected into use cases via `@Inject constructor`, never into presenters directly
- Name: `[Domain][Concept]Service`

## Domain Errors <!-- 19 -->

Typed exceptions thrown from the domain boundary. Repository implementations map transport errors to these before returning.

```kotlin
// domain/exception/DomainException.kt
sealed class DomainException(message: String) : Exception(message) {
    class Unauthorized(message: String = "Unauthorized") : DomainException(message)
    class NotFound(message: String = "Resource not found") : DomainException(message)
    class NetworkError(message: String = "Network unavailable") : DomainException(message)
    class Unknown(message: String = "Unknown error") : DomainException(message)
}
```

Rules:
- Sealed class — exhaustive `when` in presenter error handling
- No transport types leak out — `ApiException`, `IOException` are mapped in `RepositoryImpl`
- Presenters catch `DomainException` subtypes via `ErrorHandler`

## Creation Order <!-- 14 -->

When building a new feature's domain layer, create files in this sequence:

```
1. domain/entity/[Feature].kt                          ← Entity (pure Kotlin data class)
2. domain/repository/[Feature]Repository.kt            ← Repository interface
3. domain/usecase/Get[Feature]UseCase.kt
   domain/usecase/Submit[Feature]UseCase.kt
   ...                                                 ← Use Case(s) (extend SingleUseCase)
4. domain/service/[Feature][Concept]Service.kt         ← Domain Service (only if needed)
```

Never create a use case before the repository interface it depends on.
