---
name: builder-pres-create-component
description: |
  Create a reusable UI component *(iOS: UITableViewCell or UICollectionViewCell)* with UIModel pattern and SnapKit layout.
user-invocable: false
---

Create a Cell following `.claude/reference/code-architecture/presentation-impl.md ## ViewController section` and UIModel Advanced Pattern.

## Steps

1. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## ViewController`; only **Read** the full file if the section cannot be located
2. **Locate** module path: `Talenta/Module/[Module]/Presentation/View/Cell/`
3. **Create** `[Feature]TableViewCell.swift` (or `CollectionViewCell`)

## Cell Pattern

```swift
final class [Feature]TableViewCell: UITableViewCell {
    static let reuseIdentifier = "[Feature]TableViewCell"

    // MARK: - UIModel
    struct UIModel {
        let title: String
        let subtitle: String
        let isHighlighted: Bool
    }

    // MARK: - Views
    private let titleLabel = UILabel()
    private let subtitleLabel = UILabel()
    private let disposeBag = DisposeBag()

    // MARK: - Init
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupViews()
    }

    required init?(coder: NSCoder) { fatalError() }

    override func prepareForReuse() {
        super.prepareForReuse()
        disposeBag = DisposeBag()  // reset subscriptions
        titleLabel.text = nil
        subtitleLabel.text = nil
    }

    // MARK: - Layout
    private func setupViews() {
        contentView.addSubview(titleLabel)
        contentView.addSubview(subtitleLabel)

        titleLabel.snp.makeConstraints { make in
            make.top.leading.trailing.equalToSuperview().inset(MpSpacing.medium)
        }
        subtitleLabel.snp.makeConstraints { make in
            make.top.equalTo(titleLabel.snp.bottom).offset(MpSpacing.small)
            make.leading.trailing.bottom.equalToSuperview().inset(MpSpacing.medium)
        }
    }

    // MARK: - Configure
    func configure(with model: UIModel) {
        titleLabel.text = model.title
        subtitleLabel.text = model.subtitle
        contentView.backgroundColor = model.isHighlighted ? .systemYellow : .clear
    }
}
```

Rules:
- UIModel is a nested struct — pure display data, no business logic
- `prepareForReuse()` must reset `disposeBag` and clear all displayed values
- SnapKit for layout — no storyboards
- Use MekariPixel tokens for spacing/radius/colors
- Mark class `final`

## Output

Confirm file path, list all UIModel fields, and note the reuseIdentifier.
