---
name: builder-pres-create-screen
description: |
  Create a Screen *(iOS: ViewController)* with StateHolder binding, SnapKit layout, and Navigator conformance.
user-invocable: false
---

Create a ViewController following `.claude/reference/code-architecture/presentation-impl.md ## ViewController section` and project conventions in `.claude/reference/project.md ## Conventions & Naming section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## ViewController`; only **Read** the full file if the section cannot be located
2. **Read** the ViewModel to understand State, Event, and Action — never guess
3. **Locate** module path: `Talenta/Module/[Module]/Presentation/ViewController/`
4. **Create** `[Feature]ViewController.swift`

## ViewController Pattern

```swift
final class [Feature]ViewController: UIViewController {
    private let viewModel: [Feature]ViewModel
    private let disposeBag = DisposeBag()

    init(viewModel: [Feature]ViewModel) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError() }

    override func viewDidLoad() {
        super.viewDidLoad()
        setupViews()
        bindViewModel()
        viewModel.emitEvent(.viewDidLoad)
    }

    private func setupViews() {
        // SnapKit layout
        view.addSubview(tableView)
        tableView.snp.makeConstraints { $0.edges.equalToSuperview() }
    }

    private func bindViewModel() {
        // State bindings
        viewModel.stateDriver
            .compactMap({ $0.dataState.data })
            .distinctUntilChanged()
            .drive(onNext: { [weak self] data in
                self?.render(data)
            })
            .disposed(by: disposeBag)

        // Action bindings (one-time)
        viewModel.actionDriver
            .drive(onNext: { [weak self] action in
                guard let self = self else { return }
                switch action {
                case .showToast(let message):
                    self.showToast(message)
                case .navigateToDetail(let model):
                    self.viewModel.navigator?.showDetail(model)
                }
            })
            .disposed(by: disposeBag)

        // User interaction → Events
        submitButton.rx.tap
            .bind(onNext: { [weak self] in
                self?.viewModel.emitEvent(.submitButtonTapped)
            })
            .disposed(by: disposeBag)
    }
}
```

Rules:
- `[weak self]` in all closures
- `distinctUntilChanged()` on all state bindings
- `.disposed(by: disposeBag)` on all subscriptions
- Use SnapKit for layout — no storyboards/xibs unless the module already uses them
- Use MekariPixel design tokens for spacing/radius/colors
- Mark class `final`

## Output

Confirm file path and list all bound State fields, handled Actions, and sent Events.
