# SendMessage — Multi-Turn Agent Interactions Initiative

**Status:** Backlog  
**Goal:** Explore using `SendMessage` to enable mid-run agent interactions — skills that reply to a paused agent without re-spawning, preserving context across multiple turns.

---

## Background

`SendMessage` resumes an **already-running** agent that is paused and waiting for input (e.g., after an `AskUserQuestion` mid-run). It is distinct from spawning a new agent: the agent retains its full in-progress context.

Current pattern in the toolkit: agents always run to completion and return a structured Decision block. The entry skill reads the block and routes. No back-and-forth.

---

## Opportunity

Some workflows may benefit from keeping an agent alive across multiple turns rather than re-spawning with accumulated context each time:

- **Iterative planning** — orchestrator asks a clarifying question mid-synthesis; skill sends the user's answer back without losing gathered findings
- **Streaming approval loops** — an agent proposes incremental steps, skill sends user feedback after each, agent adjusts in-place
- **Long-running workers** — worker surfaces a decision point mid-execution; skill sends the choice without a full re-spawn + context relay

---

## Tradeoffs

| Approach | Pro | Con |
|---|---|---|
| Re-spawn with context relay (current) | Simple, predictable, no agent state leakage | Context grows with each round; re-spawn overhead |
| SendMessage to paused agent | Agent retains full state; no context relay | Agent must be designed to pause at the right moment; harder to reason about agent lifecycle |

---

## Prerequisite

Agent must explicitly pause (via `AskUserQuestion` or equivalent) for `SendMessage` to be useful. Agents that run straight to completion cannot be resumed — attempting to `SendMessage` a finished agent causes an error (observed in builder-plan-feature logs, 2026-05-21).

---

## Next Step

Identify a concrete workflow in the builder persona where re-spawn overhead is measurably costly, then prototype a paused-agent pattern there first.
