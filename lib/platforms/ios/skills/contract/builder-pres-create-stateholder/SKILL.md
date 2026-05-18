---
name: builder-pres-create-stateholder
description: |
  Create a StateHolder *(iOS: ViewModel)* with State/Event/Action pattern, RxSwift, and DI wire-up.
user-invocable: false
---

> **iOS mapping**: StateHolder = ViewModel (BaseViewModelV2 subclass)

Create a StateHolder (ViewModel) following `.claude/reference/code-architecture/presentation-impl.md ## State Management section` and DI rules in `.claude/reference/code-architecture/di-impl.md ## DI Principles section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## State Management` and `.claude/reference/code-architecture/di-impl.md` for `## DI Principles`; only **Read** a file in full if the section cannot be located
2. **Read** the relevant UseCase protocol signatures (never guess)
3. **Locate** module path: `Talenta/Module/[Module]/Presentation/ViewModel/`
4. **Create** `[Feature]ViewModel.swift`
5. **Wire** into the module's `DIContainer`

## ViewModel Pattern

```swift
final class [Feature]ViewModel: BaseViewModel {

    // MARK: - State
    struct State {
        var dataState: DataState<[Feature]Model> = .idle
        var isLoading: Bool = false
        // add feature-specific fields
    }

    // MARK: - Event (input from ViewController)
    enum Event {
        case viewDidLoad
        case itemSelected([Feature]Model)
        case submitButtonTapped
    }

    // MARK: - Action (one-time notifications to ViewController)
    enum Action {
        case showToast(String)
        case navigateToDetail([Feature]Model)
    }

    // MARK: - Dependencies
    private let useCase: [HttpMethod][Feature]UseCaseProtocol
    private weak var navigator: [Feature]NavigatorProtocol?

    init(useCase: [HttpMethod][Feature]UseCaseProtocol,
         navigator: [Feature]NavigatorProtocol?) {
        self.useCase = useCase
        self.navigator = navigator
        super.init()
        setBinders()
    }

    override func emitEvent(_ event: Event) {
        switch event {
        case .viewDidLoad:
            loadData()
        case .itemSelected(let item):
            handleItemSelected(item)
        case .submitButtonTapped:
            submit()
        }
    }

    private func setBinders() {
        // reactive chains triggered by relays/subjects
    }

    private func loadData() {
        updateDataState(.loading)
        let params = Get[Feature]UseCase.Params()
        useCase.call(params: params) { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .success(let model):
                self.updateDataState(.loaded(model))
            case .failure(let error):
                self.updateDataState(.error(error))
            }
        }
    }
}
```

Rules:
- `State` is a struct with value semantics — updated via `updateDataStateWith`
- `Event` is input-only — ViewController sends these
- `Action` is output-only for one-time UI effects (toasts, navigation)
- `[weak self]` in all closures
- Mark class `final`
- Never skip layers: ViewModel → UseCase → Repository

## DI Wire-up

```swift
lazy var [feature]ViewModel: [Feature]ViewModel = {
    [Feature]ViewModel(
        useCase: self.[feature]UseCase,
        navigator: self.[feature]Navigator
    )
}()
```

## Output

Confirm file path, list all State fields, Event cases, Action cases, and DI factory method.
