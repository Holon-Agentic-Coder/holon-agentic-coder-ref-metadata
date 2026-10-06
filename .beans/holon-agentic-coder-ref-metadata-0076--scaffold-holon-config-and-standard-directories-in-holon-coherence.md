---
# holon-agentic-coder-ref-metadata-0076
title: "Scaffold holon-config and standard Holon directories in holon-coherence"
status: completed
type: task
priority: normal
created_at: 2026-10-09T08:06:00Z
updated_at: 2026-10-09T09:07:00Z
---

## Summary

`holon-coherence` is missing standard Holon control plane and knowledge scaffolding directories that exist in
`holon-agentic-coder`, notably `holon-config/` (`world/`, `metrics/`, `prompts/`) and knowledge subdirectories
(`holon-knowledge/kb/`, `holon-knowledge/plans/`). This causes planning and calibration engines to lack repository-local
configuration (`ev_config.json`, `ruleset.md`, `constraints.md`), while plans cite these paths in prose.

This task scaffolds the standard Holon directories in `holon-coherence` using the `holon init` framework logic,
customized for the `holon-coherence` environment.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- Initialize `holon-config/` in `holon-coherence`:
  - `holon-config/world/ruleset.md` (defining Python 3.13+, PEP 8, strict typing, pytest standards for coherence)
  - `holon-config/world/constraints.md` (defining branch isolation, containment, and ledger immutability)
  - `holon-config/metrics/` (`ev_config.json`, `entropy_config.json`, `system_entropy_config.json`, `README.md`)
  - `holon-config/prompts/` (`planner.template.md`, `executor.template.md`)
- Ensure `holon-knowledge/` subdirectories exist:
  - `holon-knowledge/kb/.gitkeep`
  - `holon-knowledge/plans/.gitkeep`
  - Preserving existing append-only ledger files (`holon-knowledge/ledger/*.jsonl`)
- Update `.gitignore` to include `.holon-cache/` if not present.
- Verify Prettier formatting (`npx prettier@3.8.4`) and test pass rates (`uv run task test`).

## Notes

- Driven through the 5-stage Holon flow on `holon-coherence`.

## Resolution

Resolved via the full 5-stage Holon Flow lifecycle on `holon-coherence`:

1. **Stage 1 (Intent)**: `I-1791533229-scaffold-holon-config-and-standard-directories/_`
2. **Stage 2 (Plan)**: `P-1791533239-antigravity-agent-gemini-3.8-flash-medium`
3. **Stage 3 (Execute)**: `E-1791533654-antigravity-agent-gemini-3.8-flash-medium` scaffolded `holon-config/`
   (`world/ruleset.md`, `world/constraints.md`, `metrics/ev_config.json`, `metrics/entropy_config.json`,
   `metrics/system_entropy_config.json`, `prompts/planner.template.md`, `prompts/executor.template.md`) and
   `holon-knowledge/` (`kb/` and `plans/` with `.gitkeep` and `README.md`).
4. **Stage 4 (PR Review Loop)**: Opened Pull Request
   [#10](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/10). All 7 GitHub Actions CI checks passed cleanly.
   3-agent reviewer ensemble consensus identified missing `.holon-cache/` pattern in `.gitignore`, missing
   `holon-config/metrics/README.md`, entropy schema alignment, and template table formatting. Applied and pushed fixes
   in commit `340079e`. Re-ran CI checks to 100% green; posted consensus **APPROVED** review to PR #10.
5. **Stage 5 (Calibration)**: Executed `holon calibrate` resulting in branch
   `I-1791533229-scaffold-holon-config-and-standard-directories/P-1791533239-antigravity-agent-gemini-3.8-flash-medium/E-1791533654-antigravity-agent-gemini-3.8-flash-medium/calibrated`
   and report `plans/P-1791533239-antigravity-agent-gemini-3.8-flash-medium_calibration.md` ($\text{Predicted EV}:
   84.24$, $\text{Actual EV}: 84.66$, $\Delta\text{EV}: +0.42$). Pushed `/calibrated` branch to `origin`.
