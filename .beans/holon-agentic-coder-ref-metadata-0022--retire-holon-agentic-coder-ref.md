---
# holon-agentic-coder-ref-metadata-0022
title: Retire and remove holon-agentic-coder-ref reference repository
status: completed
type: task
created_at: 2026-09-17T00:00:00Z
updated_at: 2026-09-27T13:05:00Z
---

Safely retire holon-agentic-coder-ref now that bootstrap is complete. Preserve relevant benchmark artifacts, remove
develop and main worktrees, delete the local clone directory, and update metadata documentation.

## Notes

- Preserved benchmark artifacts and real trace evaluation runner in todo/.
- Removed develop and main worktrees and deleted holon-agentic-coder-ref/.
- Updated AGENTS.md, README.md, .agents/rules.md, and .agents/workflows.md to remove ref repo references.

## Assignment

Assignee: `antigravity`

## Resolution

Safely archived all uncommitted benchmark research artifacts (ab_measure_all_methods.py, scorecard_report_empirical.md,
artifacts/, openbrain/) from holon-agentic-coder-ref/develop/todo/ into the metadata todo/ scratchpad directory. Cleanly
removed git worktrees (develop and main) and deleted the local clone of holon-agentic-coder-ref/. Updated AGENTS.md,
README.md, .agents/rules.md, and .agents/workflows.md to formally retire the reference repository from active managed
targets and checklists.

## Status Audit (2026-09-27) -- `completed` stands, but one shipped default survived

Re-checked against the current tree: this bean's scope was the harness -- worktrees removed, local clone deleted, and
`AGENTS.md` / `README.md` / `.agents/rules.md` / `.agents/workflows.md` updated -- all of which holds. One reference to
the retired repository survives **in shipped code**, outside this bean's scope:
`apps/sandbox-executor/src/sandbox_executor/agent_runner.py:548` and `:550` (`get_repo_url()`) still default to
`Holon-Agentic-Coder/holon-agentic-coder-ref`, so a flow run without `HOLON_REPO_URL` targets a repository that no
longer exists. Tracked as Bean 0019 acceptance criterion 4 -- do not re-open this bean for it.
