# iOS — Syntax Conventions

Cross-cutting coding rules applied to every artifact the builder worker creates, regardless of layer.

---

## Null Safety Extensions <!-- 44 -->

```swift
// Core/Extensions/Optional+NullSafety.swift

extension Optional where Wrapped: Numeric {
    func orZero() -> Wrapped { self ?? 0 }
    func orDefault(_ defaultValue: Wrapped) -> Wrapped { self ?? defaultValue }
}

extension Optional where Wrapped == String {
    func orEmpty() -> String { self ?? "" }
    func orDefault(_ defaultValue: String) -> String {
        guard let self = self, !self.trimmingCharacters(in: .whitespaces).isEmpty else {
            return defaultValue
        }
        return self
    }
}

extension Optional where Wrapped: Collection {
    func orEmpty() -> Wrapped { self ?? [] as! Wrapped }
    var isNilOrEmpty: Bool { self?.isEmpty ?? true }
}

extension Optional where Wrapped == Bool {
    func orFalse() -> Bool { self ?? false }
    func orTrue() -> Bool { self ?? true }
}

extension Optional {
    func orDefault(_ factory: @autoclosure () -> Wrapped) -> Wrapped { self ?? factory() }
    @discardableResult
    func orElse(_ action: () -> Wrapped) -> Wrapped { self ?? action() }
}
```

**Critical:** Wrap optional chains in parentheses before calling extension methods:
```swift
($0.dataState.data?.title).orEmpty()     // ✅
$0.dataState.data?.title.orEmpty()       // ❌ compile error
```

Raw `??` is allowed only in infrastructure/extension implementations themselves, not in domain, data, or presentation code.
