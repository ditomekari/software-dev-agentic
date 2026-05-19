# Worktree Isolation Initiative

**Status:** Planning
**Goal:** Run each feature build in a dedicated git worktree so the main working tree stays clean while long-running or multi-session epics are in progress.

---

## Problem

Long-running epics (multi-session, large artifact count) currently execute directly on the active branch. This causes:

- Half-implemented features visible on the working branch during execution
- If the session is interrupted, the branch is left in a partially written state
- No isolation between concurrent feature work on the same repo
- On context compaction recovery, the worker resumes on the same branch with no safety boundary — a bad recovery can corrupt already-written artifacts

---

## Proposed Solution

When `builder-plan-feature` is approved, create a dedicated git worktree for the feature before handing off to `builder-feature-worker`. The worker operates entirely inside that worktree. On completion, the caller merges or raises a PR from the worktree branch.

The `EnterWorktree` / `ExitWorktree` tools already exist in the platform — the plumbing is available.

---

## Design

### Worktree lifecycle

| Step | Actor | Action |
|---|---|---|
| Plan approved | `builder-plan-feature` skill | Call `EnterWorktree` → creates branch `feature/<name>` + isolated worktree |
| Execution | `builder-feature-worker` | Operates entirely within the worktree path |
| Completion | `builder-plan-feature` skill | Call `ExitWorktree` → returns worktree path + branch name to user |
| Merge / PR | User | Merges the worktree branch manually or raises PR |

### Branch naming

```
feature/<feature-name>
```

Derived from the `feature` key in plan.md frontmatter.

### State file path

state.json and run artifacts live at:
```
<worktree-root>/.claude/agentic-state/runs/<feature>/
```

This keeps state co-located with the code being written, which simplifies resume after interruption.

### Resume behavior

On context compaction or session interruption, the worker reads state.json to identify `next_artifact` and resumes from that checkpoint within the same worktree branch. The worktree is not destroyed until the user explicitly merges or discards.

---

## Affected Components

| File | Change |
|---|---|
| `lib/core/skills/builder-plan-feature/SKILL.md` | Add `EnterWorktree` call after plan approval (Step 5), `ExitWorktree` after worker completes |
| `lib/core/agents/builder/builder-feature-worker.md` | Accept worktree root path as input; use it to resolve all Write/Edit paths |
| `lib/core/skills/builder-build-feature/SKILL.md` | Same `EnterWorktree` / `ExitWorktree` framing as above |

---

## Open Questions

1. **Parallel features** — if two features are in-flight simultaneously, each gets its own worktree branch. Are there any DI or code-gen conflicts that arise from diverged branches modifying the same service locator file?
2. **Cleanup policy** — who owns `ExitWorktree` on discard? The discard path in `builder-plan-feature` already runs `rm -rf runs/<feature>`. Should it also destroy the worktree branch?
3. **Code generation** — `melos run generate` / `build_runner` runs in the worktree. Does the worktree need its own `pubspec` resolution or does it inherit the parent workspace?

---

## Dependencies

- `EnterWorktree` / `ExitWorktree` tools available in current platform
- `builder-plan-feature` skill refactor to own the worktree lifecycle
- Checkpoint fix (`next_artifact` written at artifact start) should land first — worktree isolation is most valuable when combined with reliable resume
