---
name: builder-data-create-mapper
description: |
  Create a Mapper protocol and implementation to convert a Response DTO to a Domain Entity.
user-invocable: false
---

Create a Mapper following `.claude/reference/code-architecture/data-impl.md ## Mappers section` and null safety utilities in `.claude/reference/code-architecture/utilities-impl.md ## Null Safety Extensions section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/data-impl.md` for `## Mappers` and `.claude/reference/code-architecture/utilities-impl.md` for `## Null Safety Extensions`; only **Read** a file in full if the section cannot be located
2. **Read** the Response DTO and Entity to understand all fields
3. **Locate** module path: `Talenta/Module/[Module]/Data/Mapper/`
4. **Create** `[Feature]ModelMapper.swift`

## Mapper Pattern

```swift
protocol [Feature]ModelMapperProtocol {
    func fromResponseToModel(from response: [Feature]Response) -> [Feature]Model
}

final class [Feature]ModelMapper: [Feature]ModelMapperProtocol {
    func fromResponseToModel(from response: [Feature]Response) -> [Feature]Model {
        return [Feature]Model(
            id: response.id.orZero(),
            name: response.name.orEmpty(),
            isActive: response.isActive.orFalse()
        )
    }
}
```

Rules:
- **Every Entity field must appear in the mapper call** — no silent defaults
- Use `.orEmpty()` / `.orZero()` / `.orFalse()` — never `?? ""`
- Wrap optional chains: `(response.nested?.field).orEmpty()`
- For list responses: map each item, filter out nils
- Mark class `final`

## Output

Confirm file path, list all mapped fields, and flag any Entity field not present in the Response.
