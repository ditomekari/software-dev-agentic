# iOS — Error Handling

> Concepts and invariants: `reference/code-architecture/error-handling-theory.md`. This file covers Swift syntax and iOS-specific patterns.

## Error Flow <!-- 16 -->

```
DataSource throws NetworkError
    ↓ caught by
Repository transforms to BaseErrorModel
    ↓ propagated via
UseCase (passes through or enriches)
    ↓ caught by
ViewModel maps to user message → Action
    ↓ rendered by
ViewController shows error UI
```

---

## Error Types <!-- 23 -->

```swift
// Shared/Domain/Entities/BaseErrorModel.swift
struct BaseErrorModel: Error {
    let status: Int?
    let message: String
    let errors: [String: [String]]?

    init(
        status: Int? = nil,
        message: String = "An error occurred",
        errors: [String: [String]]? = nil
    ) {
        self.status = status
        self.message = message
        self.errors = errors
    }
}
```

---

## Result Type <!-- 16 -->

```swift
Result<Model, BaseErrorModel>

// Success
expected(.success(model))

// Failure
expected(.failure(BaseErrorModel(message: "Network error")))
```

All UseCase/Repository completions use `Result<Model, BaseErrorModel>`.

---

## Error Mapping <!-- 22 -->

```swift
// Shared/Data/Mapper/BaseErrorModelMapper.swift
class BaseErrorModelMapper {
    func fromResponseToModel(from error: TalentaBaseError) -> BaseErrorModel {
        return BaseErrorModel(
            status: error.status,
            message: error.message.orEmpty(),
            errors: error.errors
        )
    }
}
```

**Pattern:**
- Map API errors to `BaseErrorModel` in repositories
- ViewModel handles result, emits actions (toast, alert)
- ViewController displays errors via actions

---

## Error UI <!-- 26 -->

ViewController observes ViewModel actions to surface errors. Platform patterns are in `UIViewController+Extensions.swift`.

```swift
// In ViewController — drive error actions from ViewModel
viewModel.actionDriver
    .drive(onNext: { [weak self] action in
        switch action {
        case .showError(let message):
            self?.showErrorAlert(message: message)
        case .showToast(let message):
            self?.showToast(message)
        case .showFieldErrors(let errors):
            self?.showValidationErrors(errors)
        default:
            break
        }
    })
    .disposed(by: disposeBag)
```

**Rules:**
- ViewModel never references UIKit — it emits typed `Action` values
- ViewController maps actions to UI calls; no business logic here
- `showErrorAlert(message:)` for blocking errors; `showToast` for non-blocking
