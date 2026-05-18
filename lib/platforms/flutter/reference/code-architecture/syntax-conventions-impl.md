# Flutter — Syntax Conventions

Cross-cutting coding rules applied to every artifact the builder worker creates, regardless of layer.

---

## Null Safety Extensions <!-- 35 -->

```dart
// core/utils/null_safety.dart

extension NullableStringX on String? {
  String orEmpty() => this ?? '';
  String orDefault(String fallback) =>
      (this == null || this!.trim().isEmpty) ? fallback : this!;
  bool get isNullOrEmpty => this == null || this!.isEmpty;
}

extension NullableNumX<T extends num> on T? {
  T orZero() => this ?? (0 as T);
  T orDefault(T fallback) => this ?? fallback;
}

extension NullableListX<T> on List<T>? {
  List<T> orEmpty() => this ?? [];
  bool get isNullOrEmpty => this == null || this!.isEmpty;
}

extension NullableBoolX on bool? {
  bool orFalse() => this ?? false;
  bool orTrue() => this ?? true;
}
```

**Usage:**
```dart
final name = employee.nickname.orEmpty();
final count = list?.length.orZero();
```

Raw `??` is allowed only in infrastructure/extension implementations themselves, not in domain, data, or presentation code.
