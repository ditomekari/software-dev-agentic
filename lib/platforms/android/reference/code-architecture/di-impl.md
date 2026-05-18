# Android — Dependency Injection (Dagger 2)

## DI Principles <!-- 7 -->

- Prefer constructor injection (`@Inject constructor`) — avoid field injection except in Activities/Fragments
- Dagger modules live in each feature's `di/` package
- `app/` composes the top-level component graph
- Use `@ContributesAndroidInjector` for activities and fragments

## Registration Order <!-- 22 -->

Dagger resolves the dependency graph at compile time, but module declarations must follow leaf-first order to keep the graph readable:

```kotlin
// TimeOffModule.kt — leaf-first registration
@Module
class TimeOffModule {
    // 1. Infrastructure — no app dependencies
    @Provides fun provideTimeOffApi(retrofit: Retrofit): TimeOffApi = retrofit.create(TimeOffApi::class.java)

    // 2. Mappers — no dependencies
    @Provides fun provideTimeOffRequestMapper(): TimeOffRequestMapper = TimeOffRequestMapper()

    // 3. Repository — depends on Api + Mapper
    @Provides fun provideTimeOffRepository(api: TimeOffApi, mapper: TimeOffRequestMapper): TimeOffRepository =
        TimeOffRepositoryImpl(api, mapper)

    // 4. Use Case — depends on Repository (provided via @Inject constructor in UseCase class)
}
```

## Scope Rules <!-- 10 -->

| Dagger scope | Use for | Lifetime |
|---|---|---|
| `@Singleton` | HTTP client (`Retrofit`), database, shared utilities | App lifetime |
| `@ActivityScoped` / feature scope | Presenters — one per Activity/Fragment | Screen lifetime |
| Unscoped (default) | Mappers, pure helpers — stateless, cheap | Per-resolution |

**Never scope a Presenter as `@Singleton`** — it holds a View reference that must be released when the Activity is destroyed. Use `@ActivityScoped` or inject via `@ContributesAndroidInjector`.

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

## Activity Binding <!-- 17 -->

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

## Testing with DI <!-- 21 -->

In unit tests, bypass Dagger entirely — instantiate the class under test directly with `@Mock` dependencies:

```kotlin
@RunWith(MockitoJUnitRunner::class)
class TimeOffRepositoryImplTest {
    @Mock lateinit var mockApi: TimeOffApi
    @Mock lateinit var mockMapper: TimeOffRequestMapper

    private lateinit var repository: TimeOffRepositoryImpl

    @Before
    fun setUp() {
        // No Dagger — construct directly with mocks
        repository = TimeOffRepositoryImpl(mockApi, mockMapper)
    }
}
```

Each test class is self-contained. Never share a Dagger component or module instance across test classes — recreate in `@Before`.
