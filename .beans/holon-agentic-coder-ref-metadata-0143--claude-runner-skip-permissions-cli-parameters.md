---
# holon-agentic-coder-ref-metadata-0143
title: "Claude runner must pass the permission bypass as CLI parameters so sandboxed stages can write files"
status: in-progress
type: bug
priority: high
tags:
  - agent-runner
  - claude
  - permissions
  - flow-bootstrap
created_at: 2026-10-23T14:40:00Z
updated_at: 2026-10-26T09:42:56Z
---

## Problem

`holon`'s claude runner (`agent_runner.py`) built `claude --model <m> -p [--settings ...]` with no permission bypass. In
print mode Claude Code refuses every file write, so on 2026-10-24 the Bean 0132 planner could not write `plans/P-*.md`
(it fell back to stdout, leaving a "permission prompt" preamble in the committed plan) and any executor would author
nothing. The Antigravity runner already gets `--dangerously-skip-permissions` from `HOLON_AGENT_SKIP_PERMISSIONS`
(default `true`); the claude runner had no equivalent.

`--allow-dangerously-skip-permissions` alone only makes bypass _available_; verified in `holon/agent-claude` that a `-p`
write is still denied until `--permission-mode bypassPermissions` is also passed.

## Scope

- `ClaudeAgentRunner` honours `HOLON_AGENT_SKIP_PERMISSIONS` (default `true`) and emits
  `--allow-dangerously-skip-permissions --permission-mode bypassPermissions` on the command line.
- The bypass is never routed through the `--settings` JSON (maintainer decision).
- Tests: default-on, explicit opt-out, ordering, coexistence with `HOLON_AGENT_SETTINGS`.

## Notes

- **Flow exception**: hand-authored outside the Holon flow on the maintainer's explicit instruction (AGENTS.md "Sole
  Change Path" exception), named in the commit message. It bootstraps the flow: every other runner was unusable on
  2026-10-24 (AGY credits exhausted, codex refresh token used, opencode key expired, pi local cap per Beans 0138/0140).
- Worktree `apps/holon-agentic-coder/fix-0143-claude-runner-skip-permissions`, branch
  `fix/0143-claude-runner-skip-permissions`, commits `ca58d1e` (runner flags) and `84b5ad8` (placeholder fix), pushed to
  `origin`.
- **Folded in on maintainer instruction (2026-10-24)**: the planner placeholder bug exposed once the Claude runner could
  write files. `planner.py` applied the partial key `{plan_id` before `{plan_id}`, so `plans/{plan_id}.md` rendered as
  `plans/P-...}.md` and holon-coherence Stage 2 failed. Replaced by `render_placeholders()` (one regex pass, every
  placeholder also matches its unmatched form, order-independent, values literal) plus `tests/test_prompt_templates.py`,
  which checks every shipped `holon-config/prompts/*.template.md` for unmatched braces. Commit `84b5ad8`;
  `uv run task test` 688 passed, lint clean. An earlier separate Bean 0144 for this was withdrawn (its orphan intent
  branch `I-1792765502-planner-plan-id-placeholder-stray-brace/_` remains on `origin`).
- Claude credentials reach the sandbox as `CLAUDE_CODE_OAUTH_TOKEN` (a `claude setup-token` subscription token) via
  `HOLON_AGENT_SETTINGS`; `ANTHROPIC_API_KEY` rejects OAuth tokens. A first-class `HOLON_AGENT_OAUTH_TOKEN` mapping in
  `role_dispatcher.sh` would remove that workaround -- candidate follow-up through the flow.

- **2026-10-26:** rebased onto `origin/main` (`e3bbd67`) and force-pushed with lease: `3e6b8b3` + `e7149a9`.
  `uv run task test` 2181 passed, lint clean. The installed `holon` (uv tool, editable) points at this worktree, and
  `holon/agent-claude:latest` was rebuilt from it (role containers run the baked `/home/holon/src` code, not the host
  install). Every claude-agent flow on 2026-10-26 (Beans 0151, 0159) ran on this build. Still no PR.

## Resolution

Pending: PR (maintainer), merge, then reinstall `holon` from `origin/main` via the `install-holon` skill.
