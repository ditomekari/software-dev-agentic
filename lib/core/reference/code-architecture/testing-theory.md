# Testing

Canonical, platform-agnostic principles for testing CLEAN Architecture layers.
Platform syntax and patterns: `reference/code-architecture/testing-impl.md` in each platform directory.

---

## Test Pyramid <!-- 18 -->

```
         ┌──────────────────┐
         │   E2E Tests      │  few — critical user journeys only
         └────────┬─────────┘
         ┌────────┴─────────┐
         │ Integration Tests│  moderate — repository + datasource wiring
         └────────┬─────────┘
         ┌────────┴─────────┐
         │   Unit Tests     │  many — use cases, mappers, domain services
         └──────────────────┘
```

**Distribution target:** unit-heavy, integration-light, e2e-minimal. A test suite with more e2e than unit tests is inverted — slow, brittle, and expensive to maintain.

---

## What to Test Per Layer <!-- 11 -->

| Layer | Test targets | What to assert |
|---|---|---|
| Domain | Use cases, domain services | Business rules, edge cases, error conditions |
| Data | Mappers, repository implementations | DTO → entity mapping correctness; error mapping from transport to domain |
| Presentation | StateHolder (ViewModel/BLoC) | State transitions for each event; correct use case calls; action emissions |
| UI | Screen rendering | Correct state → UI binding; event dispatch on user interaction |

---

## Repository Tests <!-- 11 -->

Repository implementation tests verify the bridge between DataSource and Domain:

- Use a test double (mock/stub) for the DataSource — not a real network or DB
- Assert that the repository maps DataSource output to the correct domain entity
- Assert that DataSource errors are caught and mapped to the correct domain error type
- One test per operation (get, create, update, delete)

---

## Mapper Tests <!-- 10 -->

Mapper tests are pure input → output assertions — the simplest tests to write:

- Provide a fully-populated DTO → assert every field maps to the correct entity field
- Provide a DTO with missing/null optional fields → assert safe defaults or null handling
- No mocks needed — mappers have no dependencies

---

## Mock vs Real <!-- 12 -->

| Use a mock/stub when… | Use a real implementation when… |
|---|---|
| The dependency has I/O (network, DB, file) | The dependency is pure (mappers, domain services) |
| The test must control exact return values | The test verifies the full integration path |
| Speed matters — unit test suite | Correctness of wiring matters — integration test |

**Never mock domain services or mappers in unit tests** — they are pure functions; test them with real inputs and outputs.

---

## Test Naming Convention <!-- 8 -->

`[unit under test]_[scenario]_[expected outcome]`

Examples:
- `getEmployeeUseCase_whenRepositoryReturnsEmployee_emitsEmployee`
- `employeeMapper_whenDtoHasNullDepartment_mapsToDefaultDepartment`
- `employeeViewModel_whenFetchFails_emitsErrorState`
