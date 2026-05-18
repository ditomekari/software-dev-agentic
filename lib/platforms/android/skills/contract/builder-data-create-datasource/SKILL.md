---
name: builder-data-create-datasource
description: |
  Create a Retrofit API service interface (datasource) for a new feature.
user-invocable: false
---

> **Android mapping**: DataSource = Retrofit API service interface (`*Api.kt`)

Create an API service following `.claude/reference/code-architecture/data-impl.md ## API Service section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/data-impl.md` for `## API Service`; only **Read** the full file if the section cannot be located
2. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/service/`
3. **Create** `[Module]Api.kt`
4. **Create** response model(s) in `data/response/[Entity]Response.kt` if not already present
5. **Add** `@Provides` entry for the API interface in the DI module

## API Service Pattern

```kotlin
// service/FeatureApi.kt
interface FeatureApi {
    @GET("v1/feature/items")
    fun getFeatureItems(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): Single<FeatureListResponse>

    @POST("v1/feature/items")
    fun createFeatureItem(
        @Body request: CreateFeatureRequest
    ): Single<FeatureResponse>
}

// data/response/FeatureResponse.kt
data class FeatureResponse(
    @SerializedName("id")
    val id: String?,
    @SerializedName("name")
    val name: String?
)
```

Rules:
- Return `Single<Response>` (RxJava 3) for all endpoints
- Use `@Query` for URL params, `@Path` for path segments, `@Body` for request body
- Response classes: all fields `val` and nullable with `@SerializedName`
- Add `@Provides fun provide[Module]Api(retrofit: Retrofit): [Module]Api` to the DI module

## Output

Confirm API interface path, response model path(s), all method signatures, and DI provider.
