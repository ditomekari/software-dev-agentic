# Builder — Skill Contract

Platform-contract skills called by `builder` persona workers. Every platform must implement all **Required** skills under `lib/platforms/<platform>/skills/contract/<name>/SKILL.md`.

---

## feature-worker

| Skill | Required |
|---|---|
| `builder-domain-create-entity` | Yes |
| `builder-domain-create-repository` | Yes |
| `builder-domain-create-usecase` | Yes |
| `builder-domain-create-service` | Yes |
| `builder-data-create-mapper` | Yes |
| `builder-data-create-datasource` | Yes |
| `builder-data-create-repository-impl` | Yes |
| `builder-pres-create-stateholder` | Yes |
| `builder-pres-create-screen` | Yes |
| `builder-pres-create-component` | Optional — omit when the platform has no reusable component abstraction |

---

## test-worker

| Skill | Required |
|---|---|
| `builder-test-create-domain` | Yes |
| `builder-test-create-data` | Yes |
| `builder-test-create-presentation` | Yes |
| `builder-test-create-mock` | Yes |
