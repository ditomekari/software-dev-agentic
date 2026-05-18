# Android — Error Handling

> Concepts and invariants: `reference/code-architecture/data-theory.md`. This file covers Android/Kotlin-specific error handling patterns.

## Error Flow <!-- 14 -->

```
DataSource (ApiException / IOException)
      ↓
RepositoryImpl  →  maps to DomainException
      ↓
UseCase         →  propagates via RxJava onError
      ↓
Presenter       →  ErrorHandler.handle() → view?.showError()
      ↓
View (Activity/Fragment)  →  shows Toast / inline error UI
```

## Error Types <!-- 11 -->

| Type | Layer | Description |
|---|---|---|
| `ApiException` | Data | HTTP error from Retrofit; carries status code |
| `IOException` | Data | Network failure (no connectivity, timeout) |
| `DomainException` | Domain | Sealed class; subtypes: `Unauthorized`, `NotFound`, `NetworkError`, `Unknown` |
| `BaseErrorModel` | Presentation | UI-facing error with user-readable message |

See `domain.md → Domain Errors` for `DomainException` definition.

## Error Response Models <!-- 25 -->

```kotlin
data class ErrorResponse(
    @SerializedName("error") val error: ErrorDetail?
)

data class ErrorDetail(
    @SerializedName("code") val code: String?,
    @SerializedName("message") val message: String?,
    @SerializedName("errors") val errors: List<FieldError>?
)

data class FieldError(
    @SerializedName("field") val field: String?,
    @SerializedName("message") val message: String?
)

class ApiException(
    val code: Int,
    val errorResponse: ErrorResponse?,
    override val message: String
) : Exception(message)
```

## Error Interceptor <!-- 21 -->

```kotlin
class ErrorInterceptor @Inject constructor(private val gson: Gson) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())
        if (!response.isSuccessful) {
            val errorBody = response.body?.string()
            val errorResponse = try { gson.fromJson(errorBody, ErrorResponse::class.java) } catch (e: Exception) { null }
            throw ApiException(
                code = response.code,
                errorResponse = errorResponse,
                message = errorResponse?.error?.message ?: "Unknown error"
            )
        }
        return response
    }
}
```

## Error Mapping <!-- 24 -->

RepositoryImpl maps transport errors to `DomainException` via `onErrorResumeNext`:

```kotlin
.onErrorResumeNext { throwable ->
    when (throwable) {
        is ApiException -> when (throwable.code) {
            401 -> Single.error(DomainException.Unauthorized())
            404 -> Single.error(DomainException.NotFound())
            else -> Single.error(throwable)
        }
        is IOException -> Single.error(DomainException.NetworkError())
        else -> Single.error(throwable)
    }
}
```

Presenter delegates to `ErrorHandler` — never inspect the error directly in the Presenter:

```kotlin
errorHandler.handle(error) { message -> view?.showError(message) }
```

## ErrorHandler <!-- 23 -->

Central error handler injected into presenters. Never call `view?.showError(error.message)` directly.

```kotlin
class FeaturePresenter @Inject constructor(
    private val useCase: GetFeatureUseCase,
    private val errorHandler: ErrorHandler
) : BasePresenter<FeatureContract.View>(), FeatureContract.Presenter {

    override fun loadData(id: String) {
        useCase.execute(GetFeatureUseCase.Params(id))
            .doOnSubscribe { view?.showLoading() }
            .doFinally { view?.hideLoading() }
            .subscribe(
                { view?.showData(it) },
                { error -> errorHandler.handle(error) { view?.showError(it) } }
            )
            .addToDisposables()
    }
}
```

## Error UI <!-- 5 -->

> Android error UI patterns not yet catalogued. Add toast/snackbar/inline error conventions here when established.

Standard pattern: `showToast(error.message.orEmpty())` for transient errors; inline `showEmptyState()` + retry button for list screens.
