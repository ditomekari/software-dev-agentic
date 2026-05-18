# Copilot Instructions — [APP_NAME]

This project follows **Clean Architecture** on **[PLATFORM]**. Apply these rules to every suggestion, completion, and generated file.

---

## Architecture Layers

```
Domain → Data → Presentation → UI
```

| Layer | Contains | Must NOT contain |
|---|---|---|
| Domain | Entities, Repository interfaces, UseCases, Services | Framework imports, Codable, API types |
| Data | DTOs, Mappers, DataSource interfaces+impls, RepositoryImpls | Domain logic, UI code |
| Presentation | StateHolder / ViewModel / BLoC | Direct API calls, UI widgets |
| UI | Screens, Components, Navigation | Business logic, state management |

Dependencies flow inward only. Domain has zero external dependencies.

---

## Creation Order

When building a new feature, always follow this sequence:

1. Domain: Entity → Repository interface → UseCase(s)
2. Data: DTO/Mapper → DataSource interface+impl → RepositoryImpl
3. Presentation: StateHolder
4. UI: Screen → Component → Navigator

Never skip or reorder layers. Each layer depends on the one above it being complete.

---

## Platform Conventions

See `.claude/reference/` for full naming conventions, patterns, and code examples:

- `.claude/reference/code-architecture/domain-theory.md` — entity and use case rules
- `.claude/reference/code-architecture/data-theory.md` — DTO, mapper, datasource rules
- `.claude/reference/code-architecture/presentation-theory.md` — state management patterns
- `.claude/reference/code-architecture/*-impl.md` — platform-specific code patterns

---

## Hard Rules

- **No framework imports in Domain** — entities must be plain [PLATFORM] types
- **No optional force-unwrap** — use extension methods (`.orEmpty()`, `.orZero()`, `.orFalse()`)
- **No direct API calls from Presentation** — always go through a UseCase
- **No business logic in UI** — screens observe state and send events only
- **Mappers live in Data layer** — they convert Response (Data) → Entity (Domain)
- **One UseCase per operation** — do not combine get/create/update in one UseCase
