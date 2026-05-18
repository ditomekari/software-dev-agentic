# Multi-AI Platform Initiative

**Status:** In Progress
**Scope:** Extend software-dev-agentic to support GitHub Copilot and Gemini CLI alongside Claude Code.

---

## Context

Teams using this toolkit are not exclusively on Claude Code. Peers use GitHub Copilot and Gemini CLI. The goal is to let any engineer — regardless of AI tool — benefit from the same project conventions, architecture rules, and layer contracts defined in `lib/`.

Claude Code setup stays unchanged. Other AI support is purely additive.

> **Note on Copilot:** GitHub Copilot has no interactive CLI equivalent to Claude Code or Gemini CLI. `gh copilot` exists but is limited to `explain` and `suggest` shell commands only. Everything in this doc refers to the Copilot IDE extension (VS Code) and the Copilot agent on GitHub.

---

## Principles × Platform Equivalence

The table below is the source of truth for what can and cannot be ported. Phases are derived from it.

Each platform is split: **Official** = primitive provided by the platform itself. **Convention** = our design built on top of that primitive.

### 1. Project Conventions

| Principle | Claude Code Official | Claude Code Convention | Gemini CLI Official | Gemini CLI Convention | Copilot Official | Copilot Convention |
|---|---|---|---|---|---|---|
| Project-level instructions | `CLAUDE.md` | — | `GEMINI.md` | — | `.github/copilot-instructions.md` | — |
| Path-specific instructions | Per-directory `CLAUDE.md` | — | Per-directory `GEMINI.md` | — | `.github/instructions/*.instructions.md` with glob patterns | — |
| Reference doc imports | `@path` syntax | — | `@path` native syntax | Import submodule reference docs via `@` in `GEMINI.md` template | None — path hints only | List reference paths as hints in instructions file |
| Override an agent | — | Real file in `agents.local/` shadows symlink | — | None — no agent system | — | Same convention — real file in `.github/agents/<name>.agent.md` shadows symlink |
| Extend an agent | — | `agents.local/extensions/<name>.md` delta file | — | None | — | None — full override only |
| Override a command | — | None — no command system | — | Same convention — real `.gemini/commands/<name>.toml` shadows symlink | — | None — no command system |
| Override a skill | — | Real dir in `skills.local/` shadows symlink | — | Same convention — real dir in `.agents/skills/<name>/` shadows symlink | — | None — no skill system |
| Override a reference doc | — | Real file in `reference.local/` shadows platform/core | — | Same convention — `@import` resolves at file system level; real file at the same path shadows the symlink | — | None |

### 2. Skills (Procedures)

| Principle | Claude Code Official | Claude Code Convention | Gemini CLI Official | Gemini CLI Convention | Copilot Official | Copilot Convention |
|---|---|---|---|---|---|---|
| User-invocable procedure | Slash commands (`/name`) | Type T / Type U taxonomy | Custom Commands — `.gemini/commands/*.toml`, invoked via `/command-name` | Map our Type T/U skills to TOML commands in `.gemini/commands/` | None | Each Type T/U skill → `.github/agents/<name>.agent.md`; invoked via `/agent <name>`; skill body → `prompt` field |
| Agent-invocable procedure | `skills:` frontmatter field | Type A taxonomy | `.agents/skills/<name>/SKILL.md` — auto-discovered by AI from `description`; not explicitly invoked | Symlink submodule platform skills into `.agents/skills/` via `setup-ai.sh` | None | Workaround — `.github/instructions/<skill-name>.instructions.md` with `applyTo:` glob; injected automatically when working on matching files. Risk: context pollution — instructions always present for matching paths, not on-demand |

| Skill preloading | `skills:` field — content injected at agent startup | — | None | None | None | None — each agent is standalone; no preloading across agents |
| Override a skill | — | Same-name real dir in `skills.local/` shadows symlink | — | Same convention — real dir in `.agents/skills/<name>/` shadows symlink | — | Same convention — real file in `.github/agents/<name>.agent.md` shadows symlink |

#### Skill Frontmatter Fields

Each platform uses a different file format and field set depending on skill type.

**Claude Code — `SKILL.md`**

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Skill identifier |
| `description` | Yes | Shown in skill list; used for routing |
| `user-invocable` | Yes | `true` = user can invoke; `false` = agent only |
| `tools` / `allowed-tools` | No | Restricts which tools the skill can use |

**Gemini CLI — auto-discovered skill `SKILL.md` (`.agents/skills/<name>/SKILL.md`)**

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Must match directory name |
| `description` | Yes — CRITICAL | Controls when AI uses the skill; must be specific with trigger keywords |

No other fields supported — model and tools are inherited from the agent's context.

**Gemini CLI — user-invocable command (`.gemini/commands/<name>.toml`)**

| Field | Required | Notes |
|---|---|---|
| `prompt` | Yes | Skill instructions; supports `<args>`, `!{shell}`, `@{file}` injection |
| `description` | No | Shown in command list |

**Copilot — user-invocable skill (`.github/agents/<name>.agent.md`)**

| Field | Required | Notes |
|---|---|---|
| `name` | No | Defaults to filename |
| `description` | Yes | Shown in agent list; used for routing |
| `prompt` | Yes | Skill instructions go here; max 30,000 characters |
| `model` | No | Override model for this skill |
| `tools` | No | List of accessible tools |
| `mcp-servers` | No | MCP server configurations |
| `target` | No | Limit availability to specific environments |

**Copilot — agent-invocable workaround (`.github/instructions/<name>.instructions.md`)**

| Field | Required | Notes |
|---|---|---|
| `applyTo` | Yes | Glob pattern — when to inject (e.g. `"**/Domain/**"`) |

Content below frontmatter is injected as context whenever a matching file is in scope. No model, tools, or invocation fields — purely declarative.

### 3. Agents (Brain / Decision-Maker)

| Principle | Claude Code Official | Claude Code Convention | Gemini CLI Official | Gemini CLI Convention | Copilot Official | Copilot Convention |
|---|---|---|---|---|---|---|
| Custom agent definition | Agent files with frontmatter | `name`, `description`, `model`, `tools`, `skills`, `agents` fields | `.agents/agents/<name>.md` — `name`, `description`, `model`, `tools`, `kind`, `temperature`, `max_turns`, `timeout_mins`, `mcpServers` | Map our agent files to `.agents/agents/`; compatible fields: `name`, `description`, `model`, `tools` | `.github/agents/*.agent.md` — `name`, `description`, `prompt`, `tools`, `mcp-servers`, `model`, `target` | Map our agent frontmatter → `.agent.md` format; generate from our agent files |
| Invoking an agent | Type T trigger skill only — direct invocation unsupported | `description:` is identity metadata, not a routing mechanism | `@agent-name` explicit syntax | — | `/agent <name>` in Copilot CLI or UI dropdown on GitHub.com | — |
| Spawning a sub-agent | `Agent` tool — isolated context window | — | Yes — each subagent has its own isolated context window | — | Implicit subagent spawning from within `prompt` | — |
| Orchestrator/worker pattern | `Agent` tool (official) | Orchestrator/worker/planner roles + explicit delegation chain. Runtime delegation via `Agent` tool. `agents:` frontmatter field is **convention only** — not in official spec, confirmed undocumented 2026-05-09; acts as a static declaration for readability/tooling, not a guaranteed runtime mechanism | Implicit routing — no `agents:` field; router delegates automatically by description | Worker role convention portable; orchestrator delegation becomes implicit routing | None — no explicit delegation chain | Prose-only workaround: define workers as `.github/agents/*.agent.md` and describe the delegation chain in the orchestrator's `prompt`. Copilot spawns implicitly — no context isolation, no handoff validation, no static worker declaration. Pattern is not reliably portable; treat as best-effort |
| Planner agent | `Agent` tool | Read-only role, produces `plan.md` — no source writes | `.agents/agents/` supports it | Read-only planner convention portable — same role, same constraints | `.github/agents/*.agent.md` — user-invocable via `/agent <name>` | Portable workaround: define `.github/agents/<name>-planner.agent.md` with read-only constraint + plan output instructions in `prompt`. User invokes via `/agent <name>-planner`, reviews `plan.md`, then proceeds. Limitations: no context isolation, no resume routing, no sub-planner parallelism |
| Layer isolation (bounded authority) | — | Worker bounded authority convention | — | Same convention — each agent's `description` and instructions scope its authority | — | Prose-portable: write layer constraints (owned files, forbidden cross-layer reads, STOP-and-name-correct-worker rule) directly into each worker agent's `prompt`. No runtime enforcement — isolation holds only if the model follows the instructions |
| DI at skill level | `skills:` frontmatter field | Platform-agnostic workers + platform-specific skills | None — no `skills:` preloading field | Partially portable — worker stays platform-agnostic; Gemini routes to the right `.agents/skills/<name>/SKILL.md` by description match instead of explicit preloading. DI pattern holds; injection mechanism is implicit | None — no skill system in agents | No real DI — skill content must be inlined directly into the worker agent's `prompt`, collapsing the abstraction (worker becomes platform-aware). Alternatively, `.github/instructions/<skill>.instructions.md` with `applyTo:` glob injects content for matching files, but that is context pollution, not on-demand invocation |

### 4. Context Management

| Principle | Claude Code Official | Claude Code Convention | Gemini CLI Official | Gemini CLI Convention | Copilot Official | Copilot Convention |
|---|---|---|---|---|---|---|
| Isolated context per agent | `Agent` tool — each spawn is a separate context window | — | Yes — each subagent has its own isolated context window | — | None | None |
| Context relay | `Agent` tool (prompt parameter) | `context.md` + `state.json` inlined into spawn prompt by trigger skill | None | Partial workaround — Custom Commands (TOML) support `@{file}` injection; a trigger command can inline `@{runs/context.md}` and `@{runs/state.json}` into the spawn prompt. Less structured than our trigger skill but the file injection mechanism exists | None | None |
| Grep-first reference loading | `Grep` tool | Convention: section offsets in reference docs, Grep before Read | Bash/shell tool — agents can run `grep` via shell | Partially portable — Grep-first discipline written into agent instructions; `<!-- N -->` section offsets still guide `Read offset+limit` via shell grep. Less clean than a dedicated tool but functional | None | Prose-only workaround — "search for the section before reading" written into agent `prompt`; no `offset+limit` precision on file reads. Purely advisory |
| Resume routing | — | Trigger skill checks runs directory, routes resume vs new; inlines context into spawn prompt | Bash/shell tool — agents can run `find` and ask the user | Partially portable — agent runs `find ... -name "state.json"` via Bash, parses results, asks user. Routing logic moves into agent body instead of a dedicated trigger skill. `state.json` pattern is portable | None | None — no shell execution, no dynamic branching, no interactive choice in agent `prompt`. Each invocation is always a fresh start |

### 5. Hooks (Automated Enforcement)

| Principle | Claude Code Official | Claude Code Convention | Gemini CLI Official | Gemini CLI Convention | Copilot Official | Copilot Convention |
|---|---|---|---|---|---|---|
| Pre-tool hook | `settings.json` hooks | Shell scripts in `lib/platforms/<platform>/hooks/` wired via `settings.json`. Blocking hooks (exit 2) used for layer isolation enforcement — e.g. block `*RepositoryImpl`/`*DataSourceImpl` imports in presentation layer on Write\|Edit | None | None | Preview — `.github/hooks/*.json` | Convert shell hooks to JSON format |
| Post-tool hook | `settings.json` hooks | Non-blocking PostToolUse hooks for auto-fix (ESLint `--fix` on `.ts`/`.tsx` on Write\|Edit) and convention warnings (missing `'use server'` in action files on Write) | None | None | Preview | Convert shell hooks to JSON format |
| Stop hook | `settings.json` hooks | — | None | None | Preview | Convert shell hooks to JSON format |
| Notification hook | `settings.json` hooks | — | None | None | Preview | Convert shell hooks to JSON format |

### 6. Architecture Reference

| Principle | Claude Code Official | Claude Code Convention | Gemini CLI Official | Gemini CLI Convention | Copilot Official | Copilot Convention |
|---|---|---|---|---|---|---|
| Shared knowledge docs | — | Reference docs live at `.claude/reference/` in the downstream project — e.g. `reference/code-architecture/domain.md` (what a UseCase IS), `reference/contract/builder/domain.md` (how it looks in platform syntax), `reference/use-response-model.md` (iOS DTO structure). Multiple agents read the same doc via Grep-first — none embed the knowledge in their own body. Update one doc → all agents that reference it pick it up | — | Reference docs can be read by Gemini agents via Bash/shell. No Grep-first offset+limit discipline — agents read files in full or use `grep` via shell. Knowledge organization is portable as a file structure; on-demand precision reading is not | — | No structured access mechanism — agent `prompt` would need to inline the knowledge, which violates the principle. Path hints can point agents at files but there is no Grep-first or offset+limit reading discipline |
| Override at project level | — | `reference.local/` real file shadows the symlink — project-specific conventions override platform/core docs without touching the submodule | — | Portable as a file convention — place a real file at the same path; Gemini agents read it via the same path. No symlink resolution mechanism; override works at the filesystem level | — | None — no structured override mechanism; agent prompts are static |
| Lean — pointer not embed | — | Convention: agent bodies reference doc paths only, never inline content. Knowledge lives in reference docs, agents Grep on demand | `@import` (live include into session) | `@import` in `GEMINI.md` pulls reference docs into the main session upfront — not on-demand per agent. Lean is harder to maintain as the imported set grows | Path hints only | Agent `prompt` must inline knowledge — no pointer-only mechanism exists. Lean principle is not portable |

### Summary

| Capability | Claude Code | Gemini CLI | GitHub Copilot |
|---|---|---|---|
| Project conventions | Official | Official | Official |
| Path-specific instructions | Official | Official | Official |
| Reference doc imports | Official | Official | None (path hints only) |
| Extension/override (agent) | Convention only | None | None |
| Extension/override (skill) | Convention only | Same convention — real dir shadows symlink in `.agents/skills/` | None |
| Extension/override (reference) | Convention only | Same convention — `@import` picks up real file override at same path | None |
| User-invocable skills | Official + Convention | Partial — Custom Commands (TOML) for explicit invocation; `.agents/skills/` for auto-discovery | Workaround — via `.github/agents/*.agent.md`, invoked via `/agent <name>` |
| Agent-auto-discovered skills | Official + Convention | Official primitive (`.agents/skills/`) — Convention for wiring submodule skills | Workaround — `.github/instructions/<name>.instructions.md` with `applyTo:` glob (context pollution risk) |
| Agent-invocable skills | Official + Convention | None | None |
| Agent spawning / isolation | Official | Official — isolated context per subagent | Partial — implicit subagents, no context isolation |
| Orchestrator/worker pattern | Convention on top of official | Partial — implicit routing instead of explicit `agents:` field | None — no explicit delegation chain |
| Hooks | Official | None | Preview only — Convention needed for format conversion |
| Context relay + resume | Convention only | None | None |
| Architecture reference system | Convention only | Partial — importable via `@path` | None |

Principles 3 (Agents), 4 (Context Management) have no equivalent on any other platform — they are Claude Code only and are not roadmapped for porting.

---

## Phases

Each phase targets a specific principle row where a gap can be closed.

### Phase 1 — Project Conventions ✅ Done

**Targets:** Principle 1

Generate the AI-native instruction file for each platform from `lib/ai-platforms/<ai>/template.md`.

| AI | Config file | Location |
|---|---|---|
| GitHub Copilot | `copilot-instructions.md` | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` | Project root |

Templates are lean — they reference paths, never embed content. Gemini uses `@import` natively; Copilot uses path hints.

**Scripts:**
- `scripts/setup-ai.sh --ai=copilot|gemini --platform=<platform>` — generates the config file
- `scripts/clean-ai.sh --ai=copilot|gemini` — removes the config file
- Both wired into `sda.sh` as `Add AI` and `Remove AI` menu options

---

### Phase 2 — Skills · Future

**Targets:** Principle 2 — user-invocable procedures · Gemini CLI + GitHub Copilot

#### Gemini CLI

Two separate primitives map to our skill types:

- **Auto-discovered** (Type A equivalent) — `.agents/skills/<name>/SKILL.md`; AI picks up by description match. Symlink submodule platform skills into `.agents/skills/` via `setup-ai.sh`.
- **User-invocable** (Type T/U equivalent) — `.gemini/commands/<name>.toml`; explicitly invoked via `/command-name`. Map our Type T/U skills to TOML commands.

**Work needed:**
- Extend `scripts/setup-ai.sh` to symlink `lib/platforms/<platform>/skills/` into `.agents/skills/`
- Add TOML generation for Type T/U skills into `.gemini/commands/`
- Test a subset (e.g. `builder-domain-create-entity`, `builder-data-create-mapper`) before full rollout

#### GitHub Copilot

No native skill primitive — workaround via the agent system:

Each Type T/U skill becomes a `.github/agents/<name>.agent.md` file. Skill body maps to the `prompt` field. User invokes via `/agent <name>` in Copilot CLI instead of `/<name>`.

**Limitations:**
- Type A (agent-invocable) has no equivalent — only user-facing skills are portable
- `prompt` max is 30,000 characters — long skills may need trimming
- No skill preloading — each agent is standalone

**Work needed:**
- Extend `scripts/setup-ai.sh` to generate `.github/agents/` from `lib/platforms/<platform>/skills/` Type T/U skills
- Generate `.github/instructions/<skill-name>.instructions.md` with `applyTo:` glob from Type A skills — workaround for agent-invocable procedures
- Test invocation via `/agent <name>` in Copilot CLI
- Accept context pollution as a known tradeoff — instructions are always injected for matching file paths, not on-demand

---

### Phase 3 — Hooks (Copilot only, blocked) · Future

**Targets:** Principle 5 — automated enforcement · GitHub Copilot only

Gemini CLI has no hook system — Phase 3 does not apply to Gemini.

Copilot hooks (preview) support the same lifecycle events as Claude Code hooks. A converter from our shell-based hooks to Copilot's JSON format (`.github/hooks/*.json`) can be built once the API stabilizes.

**Blocked on:** Copilot hooks API moving out of preview.

---

## Progress

| Phase | Status | Notes |
|---|---|---|
| Phase 1 — Project Conventions | ✅ Done | Templates, scripts, and `sda.sh` integration shipped |
| Phase 2 — Skills (Gemini CLI) | ✅ Done | `setup-ai.sh` symlinks Type A contract skills → `.agents/skills/`; generates TOML for Type T/U → `.gemini/commands/` |
| Phase 2 — Skills (Copilot) | ✅ Done | `setup-ai.sh` generates `.agent.md` for Type T/U → `.github/agents/`; `.instructions.md` for Type A → `.github/instructions/` with derived `applyTo:` glob |
| Phase 3 — Hooks (Copilot) | ⏸ Blocked | Waiting on Copilot hooks API moving out of preview |

### Research completed — 2026-05-09

All platform capabilities verified before implementation. Key findings that shaped the plan:

- **Gemini CLI** has a full subagent system (`.agents/agents/`) with isolated context windows, `@agent-name` invocation, and rich frontmatter (`name`, `description`, `model`, `tools`, `temperature`, `max_turns`). Orchestrator/worker convention is portable — routing is implicit rather than explicit `agents:` field.
- **Gemini CLI** has two distinct skill primitives: auto-discovered skills (`.agents/skills/SKILL.md`, `name`+`description` only) and user-invocable Custom Commands (`.gemini/commands/*.toml`). Our Phase 2 must target both.
- **GitHub Copilot** has a real invocable agent system (`.github/agents/*.agent.md`, `/agent <name>`). Type T/U skills map to agents; Type A skills have a workaround via `.github/instructions/*.instructions.md` with `applyTo:` glob — context pollution is an accepted tradeoff.
- **GitHub Copilot** has no native skill invocation primitive — the agent system is the only workaround.
- **Type B** skill type retired from our taxonomy — automated bash belongs in hooks, not skills. All 5 misclassified iOS skills migrated to Type U.
- **Natural language routing** removed from our principles — trigger skills are the only supported entry path.

---

## References

- [GitHub Copilot custom instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [GitHub Copilot custom agents](https://docs.github.com/en/copilot/concepts/agents)
- [GitHub Copilot — creating custom agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents)
- [GitHub Copilot CLI — custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [GitHub Copilot hooks (preview)](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-hooks)
- [Gemini CLI — GEMINI.md](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html)
- [Gemini CLI — Agent Skills](https://codelabs.developers.google.com/gemini-cli/how-to-create-agent-skills-for-gemini-cli)
- [Gemini CLI — Custom Commands](https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html)
- [Gemini CLI — Subagents](https://geminicli.com/docs/core/subagents/)
- [Gemini CLI — Agent Skills](https://geminicli.com/docs/cli/skills/)
