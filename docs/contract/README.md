# docs/contract/

Contracts that define the base spec for platform resources. Each file specifies what a platform must implement — consumed by both the **builder** persona (grep targets when reading reference files) and the **auditor** persona (enforcement via `arch-check-conventions`).

## Files

| File | Owned by | Defines |
|---|---|---|
| `builder-auditor-schema.md` | Builder + Auditor | Required `##` keyword headings for all 8 platform reference contract files |
| `builder-skill-contract.md` | Builder | Required contract skills for `feature-worker` and `test-worker` |
| `detective-skill-contract.md` | Detective | Required contract skills for `debug-log-worker` |
| `auditor-skill-contract.md` | Auditor | Required contract skills for `arch-review-worker` |
| `installer-skill-contract.md` | Installer | Required contract skills for `setup-worker` |

---

## Platform Reference Contract Structure

Every file under `lib/platforms/<platform>/reference/contract/<persona>/` must follow this heading structure:

- `#` — platform + topic title (e.g. `# Flutter — Domain Layer`)
- `##` — canonical section headings (greppable by agents)
- `###` and deeper — subsections within a canonical section

Platforms may add platform-specific `##` sections and adapt content to their syntax — but every required keyword must be in a `##` heading.

**Core templates** — each contract file has a platform-agnostic counterpart in `lib/platforms/<platform>/reference/code-architecture/<filename>` that defines concepts and invariants. Platform files implement those concepts in their own syntax. Currently available: `domain.md`, `data.md`, `presentation.md`, `ui.md`, `di.md`, `testing.md`, `error-handling.md`.

---

## How to validate skills

```bash
# Check all platforms
software-dev-agentic/scripts/check-skill-contracts.sh

# Check one platform
software-dev-agentic/scripts/check-skill-contracts.sh --platform=flutter
```

Exits non-zero if any Required skill is missing — safe to run in CI. Also runs automatically at the end of `setup-symlinks.sh`.

---

## How to validate reference headings

```bash
# Check one file — exits non-zero if any keyword is missing
for keyword in "Entities" "Repository" "Use Cases" "Services" "Domain Errors"; do
  grep -q "^## .*$keyword" lib/platforms/web/reference/code-architecture/domain.md \
    || echo "MISSING: $keyword"
done
```

`arch-check-conventions` enforces this automatically for all three platforms.

---

## Adding a new platform

These 8 reference contract files are a **prerequisite for the builder and auditor personas to function** on any platform:

- **Builder** workers (`domain-worker`, `data-worker`, `presentation-worker`, etc.) grep canonical keywords from these files as their reference targets — missing headings mean workers can't find the patterns they need
- **Auditor** (`arch-check-conventions`) enforces keyword presence — a platform without these files will fail every convention check

When adding a 4th platform:
1. Create `lib/platforms/<platform>/reference/code-architecture/` with all 8 files
2. Each file must contain the required keywords defined in `builder-auditor-schema.md`
3. Run `arch-check-conventions` on the new platform's contract directory to verify compliance before merging
