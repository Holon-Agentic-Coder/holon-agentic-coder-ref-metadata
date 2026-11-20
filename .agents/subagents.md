# Subagent Invocation & AGY Runtime

How to delegate to subagents and the Antigravity runtime. Moved verbatim from `AGENTS.md`.

---

## 🤖 Subagent Invocation & AGY Runtime

Subagent delegation in this ecosystem is primarily targeted towards the **Antigravity (AGY)** runtime:

- **Invocation Tool**: Use the `invoke_subagent` tool to spawn child tasks, isolated review passes, and resolution
  passes.
- **Subagent Type**: Specify `TypeName: "self"` to inherit the full suite of parent capabilities, tools (file viewing,
  editing, command execution), instructions, and credentials. Use `TypeName: "research"` for read-only exploratory
  research.
- **Model Selection & Automatic Credit Fallback**: Set `Model: "inherit"` by default to inherit the parent agent's
  active model configuration. If credit or quota runs out on the higher-level model (`"inherit"` / `"pro"`),
  automatically fall back to `"flash"` and then `"flash_lite"` (and similarly step down `claude-fable-5` $\rightarrow$
  `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6` $\rightarrow$ `claude-haiku-4-5` or `gemini-3.8-pro-high`
  $\rightarrow$ `gemini-3.8-flash-medium` $\rightarrow$ `gemini-3.8-flash` in `holon` CLI invocations) and continue the
  flow or review loop from the current stage without discarding completed work.
- **Reactive Wakeup (Zero Polling)**: The AGY runtime automatically wakes up the parent agent upon subagent completion
  or message delivery. Never poll or loop on subagent status.
- **Generic Coding Agent Compatibility**: Skill workflows (such as `pr-review-loop`) define generic subagent task
  contracts so any coding agent (Claude Code, Codex, Pi, OpenCodeInterpreter) can spin off subagents using its native
  delegation mechanism (child process, task tool, or isolated session), while retaining explicit AGY invocation
  parameters for seamless native execution.

---
