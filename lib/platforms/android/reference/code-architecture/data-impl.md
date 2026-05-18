# Android — Data Layer

> Concepts and invariants: `reference/code-architecture/data-theory.md`. This file covers Kotlin/Android-specific data layer patterns.

## DTOs <!-- 34 -->

Android calls these **Response Models** (`*Response` suffix, placed in `data/response/`). Same contract as core — raw API shape, all fields nullable, `@SerializedName` for every field, no business logic. Never returned from repository — always mapped to an entity first.

```kotlin
// data/response/TimeOffRequestListResponse.kt
data class TimeOffRequestListResponse(
    @SerializedName("data") val data: List<TimeOffRequestResponse>?,
    @SerializedName("meta") val meta: MetaResponse?
)

data class TimeOffRequestResponse(
    @SerializedName("id") val id: String?,
    @SerializedName("employee_id") val employeeId: String?,
    @SerializedName("start_date") val startDate: String?,
    @SerializedName("end_date") val endDate: String?,
    @SerializedName("reason") val reason: String?,
    @SerializedName("status") val status: String?,
    @SerializedName("total_days") val totalDays: Int?
)

data class MetaResponse(
    @SerializedName("total") val total: Int?,
    @SerializedName("page") val page: Int?,
    @SerializedName("limit") val limit: Int?
)
```

Rules:
- All fields `val` and nullable (`?`) — server may omit any field
- Use `@SerializedName` for every field
- No business logic in response models
- Class suffix is `*Response`; file lives in `data/response/`

## Mappers <!-- 35 -->

Extend `BaseMapper<Response, Entity>` — map every entity field, use null-safety extensions.

```kotlin
// data/mapper/TimeOffRequestMapper.kt
import com.mekari.commons.extension.orEmpty
import com.mekari.commons.extension.orZero

class TimeOffRequestMapper : BaseMapper<TimeOffRequestResponse, TimeOffRequest> {
    override fun map(input: TimeOffRequestResponse): TimeOffRequest {
        return TimeOffRequest(
            id = input.id.orEmpty(),
            employeeId = input.employeeId.orEmpty(),
            startDate = input.startDate.orEmpty(),
            endDate = input.endDate.orEmpty(),
            reason = input.reason.orEmpty(),
            status = input.status.orEmpty(),
            totalDays = input.totalDays.orZero()
        )
    }

    fun mapList(responses: List<TimeOffRequestResponse>?): List<TimeOffRequest> {
        return responses?.map { map(it) } ?: emptyList()
    }
}
```

Rules:
- **Every entity field must appear in the mapper call** — no silent defaults
- Use `.orEmpty()` for String/List, `.orZero()` for Int/Long/Double, `.orFalse()` or `.orTrue()` for Boolean
- Never use `?: ""` or `?: 0` — always the extension function
- Add `mapList(responses: List<Response>?)` helper for list mappings
- For nested objects: create a nested mapper class

## Data Sources <!-- 28 -->

Android implements the DataSource contract as a **Retrofit interface** (`*Api` suffix, placed in `service/`). The interface is the abstraction; Retrofit generates the implementation at runtime via Dagger injection — no separate `*Impl` class needed.

```kotlin
// service/TimeOffApi.kt
interface TimeOffApi {
    @GET("v1/time-off/requests")
    fun getTimeOffRequests(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): Single<TimeOffRequestListResponse>

    @POST("v1/time-off/requests")
    fun submitTimeOffRequest(
        @Body request: SubmitTimeOffRequest
    ): Single<TimeOffRequestResponse>

    @DELETE("v1/time-off/requests/{id}")
    fun deleteTimeOffRequest(@Path("id") id: String): Completable
}
```

Rules:
- Return `Single<Response>` for endpoints with response body; `Completable` for DELETE/void endpoints
- Use `@Query` for URL params, `@Path` for path segments, `@Body` for request body
- One interface per feature module

## Repository Implementation <!-- 38 -->

Implement domain repository interface — inject API and mapper via Dagger.

```kotlin
// data/repoimpl/TimeOffRepositoryImpl.kt
class TimeOffRepositoryImpl @Inject constructor(
    private val api: TimeOffApi,
    private val mapper: TimeOffRequestMapper
) : TimeOffRepository {

    override fun getTimeOffRequests(page: Int, limit: Int): Single<List<TimeOffRequest>> {
        return api.getTimeOffRequests(page, limit)
            .map { response -> mapper.mapList(response.data) }
            .onErrorResumeNext { throwable ->
                when (throwable) {
                    is ApiException -> when (throwable.code) {
                        401 -> Single.error(UnauthorizedException())
                        404 -> Single.error(NotFoundException())
                        else -> Single.error(throwable)
                    }
                    is IOException -> Single.error(NetworkException())
                    else -> Single.error(throwable)
                }
            }
    }

    override fun deleteTimeOffRequest(id: String): Completable {
        return api.deleteTimeOffRequest(id)
    }
}
```

Rules:
- `@Inject constructor` — Dagger provides all dependencies
- Use `mapper.mapList(response.data)` for list responses
- Map `ApiException` to domain exceptions via `onErrorResumeNext`
- Never expose response types outside the data layer
