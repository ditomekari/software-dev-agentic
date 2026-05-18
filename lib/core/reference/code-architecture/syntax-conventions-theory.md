# Syntax Conventions

Cross-cutting coding rules enforced by the builder worker across every artifact, regardless of layer or platform. Platform implementations live in `reference/code-architecture/syntax-conventions-impl.md`.

---

## Null Safety Extensions <!-- 20 -->

**Rule:** Never use raw null-fallback operators (e.g. `??`, `?:`, `!`) directly in domain, data, or presentation code. Always delegate to a named extension method or utility function.

**Why:** Raw operators scatter fallback semantics across the codebase — the intent (`orEmpty`, `orZero`) disappears into punctuation. Named methods make the fallback explicit, searchable, and consistently applied.

**Categories — every platform must implement all of these:**

| Category | Method name | Fallback |
|---|---|---|
| Nullable numeric | `orZero()` | `0` |
| Nullable string | `orEmpty()` | `""` |
| Nullable collection | `orEmpty()` | `[]` |
| Nullable bool (false) | `orFalse()` | `false` |
| Nullable bool (true) | `orTrue()` | `true` |
| Nullable with custom default | `orDefault(x)` | `x` |

**Invariant:** Raw null operators are allowed only inside the extension/utility implementations themselves — never in domain, data, or presentation artifacts.

**Platform implementations:** See `reference/code-architecture/syntax-conventions-impl.md` for the platform-specific code.
