# Android — Dependency Injection (Dagger 2)

## DI Principles <!-- 7 -->

- Prefer constructor injection (`@Inject constructor`) — avoid field injection except in Activities/Fragments
- Dagger modules live in each feature's `di/` package
- `app/` composes the top-level component graph
- Use `@ContributesAndroidInjector` for activities and fragments

## DI Module <!-- 27 -->

```kotlin
// di/TimeOffModule.kt
@Module
class TimeOffModule {

    @Provides
    fun provideTimeOffApi(retrofit: Retrofit): TimeOffApi {
        return retrofit.create(TimeOffApi::class.java)
    }

    @Provides
    fun provideTimeOffRequestMapper(): TimeOffRequestMapper {
        return TimeOffRequestMapper()
    }

    @Provides
    fun provideTimeOffRepository(
        api: TimeOffApi,
        mapper: TimeOffRequestMapper
    ): TimeOffRepository {
        return TimeOffRepositoryImpl(api, mapper)
    }
}
```

## Activity Binding <!-- 16 -->

```kotlin
// di/TimeOffActivityModule.kt
@Module
abstract class TimeOffActivityModule {

    @ContributesAndroidInjector(modules = [TimeOffModule::class])
    abstract fun contributeTimeOffRequestActivity(): TimeOffRequestActivity
}
```

Rules:
- Register `TimeOffActivityModule` in the app-level `ActivityModule` or equivalent binding module
- Presenter is injected by Dagger via `@Inject` — declare it as `@Inject lateinit var presenter` in the activity
- Do not instantiate any injectable class with `MyClass()`; always let Dagger provide it
