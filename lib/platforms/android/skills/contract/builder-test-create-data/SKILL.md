---
name: builder-test-create-data
description: |
  Generate unit tests for a Mapper covering valid response, null fields, and list mapping cases.
user-invocable: false
---

Create Data layer tests following `.claude/reference/code-architecture/testing-impl.md ## Mapper Tests section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/testing-impl.md` for `## Mapper Tests`; only **Read** the full file if the section cannot be located
2. **Read** the Mapper class, Response model, and Entity to understand all fields
3. **Locate** test path: `feature_[module]/src/test/java/co/talenta/feature_[module]/data/mapper/`
4. **Create** `[Entity]MapperTest.kt`

## Mapper Test Pattern

```kotlin
@RunWith(MockitoJUnitRunner::class)
class FeatureEntityMapperTest {

    private lateinit var mapper: FeatureEntityMapper

    @Before
    fun setUp() { mapper = FeatureEntityMapper() }

    @Test
    fun test_givenValidResponse_whenMap_thenEntityIsCorrect() {
        // given
        val response = FeatureResponse(id = "1", name = "Test", count = 5, isActive = true)

        // when
        val result = mapper.map(response)

        // then
        assertEquals("1", result.id)
        assertEquals("Test", result.name)
        assertEquals(5, result.count)
        assertTrue(result.isActive)
    }

    @Test
    fun test_givenNullFields_whenMap_thenDefaultsApplied() {
        // given
        val response = FeatureResponse(null, null, null, null)

        // when
        val result = mapper.map(response)

        // then
        assertEquals("", result.id)
        assertEquals("", result.name)
        assertEquals(0, result.count)
        assertFalse(result.isActive)
    }

    @Test
    fun test_givenListResponse_whenMapList_thenAllEntitiesMapped() {
        // given
        val responses = listOf(
            FeatureResponse("1", "Feature 1", 1, true),
            FeatureResponse("2", "Feature 2", 2, false)
        )

        // when
        val results = responses.map { mapper.map(it) }

        // then
        assertEquals(2, results.size)
        assertEquals("1", results[0].id)
        assertEquals("2", results[1].id)
    }
}
```

## Coverage Targets

- `test_givenValidResponse_whenMap_thenEntityIsCorrect` — all fields populated correctly
- `test_givenNullFields_whenMap_thenDefaultsApplied` — every nullable field maps to its default
- `test_givenListResponse_whenMapList_thenAllEntitiesMapped` — list size and identity preserved

## Output

Confirm test file path and list all test method names.
