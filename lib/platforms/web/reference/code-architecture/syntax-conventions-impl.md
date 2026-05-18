# Web — Syntax Conventions

Cross-cutting coding rules applied to every artifact the builder worker creates, regardless of layer.

---

## Null Safety Extensions <!-- 37 -->

```typescript
// core/utils/nullSafety.ts

/** Returns the value or 0 if null/undefined */
export function orZero(value: number | null | undefined): number {
  return value ?? 0;
}

/** Returns the value or empty string if null/undefined */
export function orEmpty(value: string | null | undefined): string {
  return value ?? '';
}

/** Returns the value or empty array if null/undefined */
export function orEmptyArray<T>(value: T[] | null | undefined): T[] {
  return value ?? [];
}

/** Returns the value or the provided default */
export function orDefault<T>(value: T | null | undefined, defaultValue: T): T {
  return value ?? defaultValue;
}

/** Filters null/undefined values from an array */
export function compact<T>(array: (T | null | undefined)[]): T[] {
  return array.filter((item): item is T => item != null);
}

/** Returns first non-null value */
export function firstNonNull<T>(...values: (T | null | undefined)[]): T | null {
  return values.find((v) => v != null) ?? null;
}
```

Raw `??` is allowed only in infrastructure/utility implementations themselves, not in domain, data, or presentation code.
