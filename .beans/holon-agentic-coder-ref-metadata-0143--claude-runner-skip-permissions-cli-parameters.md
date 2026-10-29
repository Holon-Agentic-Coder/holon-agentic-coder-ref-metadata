---
# holon-agentic-coder-ref-metadata-0143
title: "Claude runner must pass the permission bypass as CLI parameters so sandboxed stages can write files"
status: completed
type: bug
priority: high
tags:
  - agent-runner
  - claude
  - permissions
  - flow-bootstrap
created_at: 2026-10-23T14:40:00Z
updated_at: 2026-10-29T04:00:00Z
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

- **2026-10-27:** every claude-agent flow so far (Beans 0151 and 0159) ran on this branch's build: the global `holon`
  tool install and `holon/agent-claude:latest`. After PR #97 merged, `main` has moved again, so rebase this branch and
  rebuild before the next claude-agent flow, or land the PR. It still has no PR.

## Resolution

Completed through the Holon flow: PR #104 merged as `cc4bf1b` (2026-10-29). `main` worktrees fast-forwarded; `holon` and
`holon-coherence` reinstalled (editable) from `main` and every image rebuilt via the `install-holon` skill;
`holon/agent-claude` carries the bypass. The hand-authored `fix/0143` branch (last tip `19a6032`) and both `0143`
worktrees are retired, superseded by the flow PR.

- **2026-10-29 — through the Holon flow:** bootstrap build from `fix/0143` (rebased onto `e187393` as `19a6032`, 2680
  passed) installed as host `holon` and baked into every image. Flow `I-1793241043` → `P-1793241058` → `E-1793241233`
  (claude-agent, 7 min) produced the fix from `main`; PR #104. Review loop 3 iterations (2 Nits applied), 3/3 approval
  and 9/9 CI at `1a51ff7` (review 5692289790), calibrated (`c3afba2`, EV 59.79 predicted, 79.26 actual), folded into the
  PR head `9bc1ed5`. After merge: install `holon` and `holon-coherence` from `main`, then retire the `fix/0143` worktree
  and branch (superseded by the flow PR).
