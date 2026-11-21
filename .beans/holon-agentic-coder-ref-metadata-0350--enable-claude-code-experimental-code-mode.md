---
# holon-agentic-coder-ref-metadata-0350
title: "Enable Claude Code code mode (CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1) for every Claude run"
status: todo
type: feature
priority: high
tags:
  - claude
  - holon-flow
  - subagents
  - harness
  - holon-agentic-coder
created_at: 2026-11-21T12:06:00+11:00
updated_at: 2026-11-21T12:06:00+11:00
---

## Problem

Claude Code added an experimental code mode, switched on with the environment variable
`CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1`. The maintainer wants it enabled for every place that runs Claude: the Holon
flow, subagents, and anything else. Nothing sets the variable today.

## Action

1. **Harness flow runner (direct edit).** `.agents/skills/holon_flow/scripts/flow_env.py` builds the environment for
   `holon flow` with `--agent claude-agent`. Add `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1` there, and keep a value the
   caller already set. Add a test in `tests/test_flow_env.py`. Document it in `.agents/skills/holon_flow/SKILL.md`.
2. **Harness Claude sessions and subagents (direct edit).** Set the variable in the project's `.claude/settings.json`
   `env` block, so interactive sessions and every subagent they spawn inherit it. Check that subagents and skills run
   through the Agent tool pick it up. Never put credentials in that file.
3. **Target containers (through the Holon flow on `holon-agentic-coder`).** The claude runner inside the sandbox
   containers must run with the variable set for every role: Stage 1-3 agents, the Stage 4 reviewers and resolver, and
   Stage 5. Candidates on `main`:
   - `agent_runner.py`
   - `agent_defaults.py`
   - `claude_credential.py`
   - the env passed to role containers
   - `entrypoint/role_dispatcher.sh`

   Make it a documented default that an operator can override (for example `HOLON_CLAUDE_CODE_MODE=0`), pass it through
   to the container, and record it in `holon doctor`. Add hermetic tests showing that the claude runner's command
   environment contains the variable and that the override turns it off.

4. **Other Claude entry points.** Check the remaining places that start `claude`: the review-loop skills, post-merge,
   resolve-conflict, holon-coherence if it runs Claude, and the dev-env shell profile if the maintainer wants it
   globally. Set the variable in each, or record why one is excluded.
5. **Verification.**
   - Run one real flow with the variable set and confirm it shows in the runner environment (never print secrets).
   - Compare token use and duration against a recent flow of similar size, and record any regressions.
   - Because the mode is experimental, note how to switch it off quickly if it misbehaves.

## Notes

- Keep it switchable, because the feature is experimental.
- Intent JSON must not name harness paths. The target-repo part goes through the Holon flow.
