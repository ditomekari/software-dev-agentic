# Android — Syntax Conventions

Cross-cutting coding rules applied to every artifact the builder worker creates, regardless of layer.

---

## Null Safety Extensions <!-- 24 -->

All extensions live in `com.mekari.commons.extension`. Import only what you use.

```kotlin
import com.mekari.commons.extension.orEmpty   // String?, List<T>?
import com.mekari.commons.extension.orZero    // Int?, Long?, Double?, Float?
import com.mekari.commons.extension.orFalse   // Boolean?
import com.mekari.commons.extension.orTrue    // Boolean?
```

Usage:
```kotlin
val name: String  = response.name.orEmpty()          // null → ""
val items: List<T> = response.items.orEmpty()        // null → emptyList()
val count: Int    = response.count.orZero()          // null → 0
val isActive: Boolean = response.isActive.orFalse()  // null → false
val isEnabled: Boolean = response.isEnabled.orTrue() // null → true
```

Rules:
- Never use `?: ""`, `?: 0`, `?: false` inline in mappers — always use the extension function
- For nested optional chains: `response.nested?.field.orEmpty()`
- For list mapping: `response.items?.map { mapper.map(it) }.orEmpty()`
