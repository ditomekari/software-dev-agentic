---
name: builder-data-create-repository-impl
description: |
  Create a RepositoryImpl in the Data layer that bridges DataSource → Mapper → Domain.
user-invocable: false
---

Create a RepositoryImpl following `.claude/reference/code-architecture/data-impl.md ## Repository Implementation section`, DI rules in `.claude/reference/code-architecture/di-impl.md ## DI Principles section`, and error handling in `.claude/reference/code-architecture/error-handling-impl.md ## Error Flow section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/data-impl.md` for `## Repository Implementation`, `.claude/reference/code-architecture/di-impl.md` for `## DI Principles`, and `.claude/reference/code-architecture/error-handling-impl.md` for `## Error Flow`; only **Read** a file in full if the section cannot be located
2. **Read** the Repository protocol, DataSource protocol, and Mapper protocol to understand signatures
3. **Locate** module path: `Talenta/Module/[Module]/Data/Repository/`
4. **Create** `[Feature]RepositoryImpl.swift`
5. **Wire** into the module's `DIContainer`

## RepositoryImpl Pattern

```swift
final class [Feature]RepositoryImpl: [Feature]RepositoryProtocol {
    private let dataSource: [Feature]DataSourceProtocol
    private let mapper: [Feature]ModelMapperProtocol

    init(dataSource: [Feature]DataSourceProtocol,
         mapper: [Feature]ModelMapperProtocol) {
        self.dataSource = dataSource
        self.mapper = mapper
    }

    func methodName(params: [UseCase].Params,
                    completion: @escaping (Result<[Model], BaseErrorModel>) -> Void) {
        dataSource.methodName(params: params) { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .success(let response):
                let model = self.mapper.fromResponseToModel(from: response)
                completion(.success(model))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
}
```

Rules:
- Bridge DataSource (Response) → Mapper → Domain (Model)
- Use `[weak self]` in all closures
- Pass errors through unchanged — never swallow
- Mark class `final`
- Note: some RepositoryImpl files exist in the Domain layer — follow existing placement for the module

## DI Wire-up

```swift
lazy var [feature]Repository: [Feature]RepositoryProtocol = {
    [Feature]RepositoryImpl(
        dataSource: self.[feature]DataSource,
        mapper: self.[feature]Mapper
    )
}()
```

## Output

Confirm file path and DI property name.
