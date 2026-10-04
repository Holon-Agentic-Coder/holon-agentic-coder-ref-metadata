---
# holon-agentic-coder-ref-metadata-0035
title: "Remove coherence executable entrypoint and retain only holon-coherence"
status: completed
type: task
priority: normal
tags:
  - packaging
  - holon-coherence
  - cli
created_at: 2026-09-26T08:58:00Z
updated_at: 2026-10-04T15:02:00Z
---

When installing `holon-coherence` via `uv tool install git+https://github.com/Holon-Agentic-Coder/holon-coherence.git`,
`uv` installs two executables: `coherence` and `holon-coherence`.

The `coherence` entrypoint was defined in `pyproject.toml` under `[project.scripts]` as an alias pointing to
`holon_coherence.cli:main`. To maintain a single unambiguous binary name and prevent naming collisions with other tools
or packages named `coherence`, remove the `coherence = "holon_coherence.cli:main"` entrypoint so only `holon-coherence`
is installed.

## Acceptance Criteria

- Remove `coherence = "holon_coherence.cli:main"` from `[project.scripts]` in `apps/holon-coherence/pyproject.toml`.
- Retain only `holon-coherence = "holon_coherence.cli:main"`.
- Verify packaging and test suites pass cleanly with `uv run pytest` and linting checks.
- Verify `uv tool install` installs only `holon-coherence`.

## Notes

- Target repository: `apps/holon-coherence/`
- Worktree & branch to be created off `origin/main` (e.g. `feat/0035-remove-coherence-entrypoint`).
- No internal CLI logic depends on `coherence`; all existing CLI commands, tests, and documentation use
  `holon-coherence`.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `apps/holon-coherence/pyproject.toml:39` still
declares `coherence = "holon_coherence.cli:main"` alongside `holon-coherence`.

## Status Re-audit (2026-09-27) -- unchanged, still `todo`

`apps/holon-coherence/main/pyproject.toml:37-39` still declares both `holon-coherence` **and** the `coherence` alias
pointing at `holon_coherence.cli:main`. Nothing on `origin/main` removes it, so `uv tool install` still lands two
binaries.

## Resolution (2026-10-04)

Executed fully within the 5-stage containerized Holon flow lifecycle targeting `holon-coherence` (via `HOLON_REPO_URL`
authentication and containerized role agents):

1. **Stage 1 (Intent Creation):** Executed `./holon intent` with intent payload
   `remove-coherence-executable-entrypoint`. Initialized intent branch
   `I-1791108912-remove-coherence-executable-entrypoint/_` and logged intent metadata into
   `holon-knowledge/ledger/intents.jsonl`.
2. **Stage 2 (Plan Generation):** Executed `./holon plan` using `antigravity-agent` (`gemini-3.8-flash-medium`). Created
   plan branch
   `I-1791108912-remove-coherence-executable-entrypoint/P-1791108931-antigravity-agent-gemini-3.8-flash-medium/_`,
   generated markdown plan `plans/P-1791108931-antigravity-agent-gemini-3.8-flash-medium.md`, and recorded to
   `holon-knowledge/ledger/plans.jsonl` (predicted EV: 82.90).
3. **Stage 3 (Plan Execution):** Executed `./holon execute` using `antigravity-agent`. Checked out execution branch
   `I-1791108912-remove-coherence-executable-entrypoint/P-1791108931-antigravity-agent-gemini-3.8-flash-medium/E-1791109052-antigravity-agent-gemini-3.8-flash-medium/_`.
   The executor agent removed `coherence = "holon_coherence.cli:main"` from `[project.scripts]` in `pyproject.toml`,
   audited repository references, validated clean wheel building, and committed the changes along with execution record
   `executions/E-1791109052-antigravity-agent-gemini-3.8-flash-medium.md` and ledger entry.
4. **Stage 4 (PR Review Loop):** Opened GitHub Pull Request #8
   (https://github.com/Holon-Agentic-Coder/holon-coherence/pull/8).
   - In Iteration 1, the 3-agent ensemble caught a CI failure in `Test - Hygiene` due to Prettier formatting differences
     in the generated plan/execution markdown.
   - Formatted all markdown using `npx prettier --write "**/*.md"` and pushed commit `7542801`.
   - In Iteration 2, all three independent reviewer subagents reached unanimous approval (`APPROVED`, 0 findings) and
     all 7 GitHub Actions CI checks turned green.
   - Synthesized and posted the ensemble consensus approval report to GitHub PR #8.
5. **Stage 5 (Calibration):** Executed `./holon calibrate`, creating branch
   `I-1791108912-remove-coherence-executable-entrypoint/P-1791108931-antigravity-agent-gemini-3.8-flash-medium/E-1791109052-antigravity-agent-gemini-3.8-flash-medium/calibrated`
   (Actual EV: 84.87, ΔEV: +1.97). Per explicit operator instruction, also carried
   `plans/P-1791108931-antigravity-agent-gemini-3.8-flash-medium_calibration.md` on top of PR #8 via commit `58a6b38`.
   All 7 GitHub Actions CI checks were verified green on the calibration commit.
6. PR #8 is fully approved and calibrated, awaiting manual merge by human maintainer per Bean 0034.
