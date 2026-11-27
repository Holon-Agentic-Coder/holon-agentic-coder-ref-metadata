---
# holon-agentic-coder-ref-metadata-0637
title: "Coherence: reject missing or stale module_budgets overrides and prune dashboard and aggregation"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - hygiene
  - module-budgets
created_at: 2026-11-27T15:53:29Z
updated_at: 2026-11-27T15:55:01Z
---

## Notes

### Evidence (2026-11-27 fifth-merge audit, `holon-coherence@4d2cfcf8`)

- [Coherence #67](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/67) (`63a6bf3f7`) extracted inline HTML
  into `src/holon_coherence/proxy/dashboard.html`, shrinking `src/holon_coherence/proxy/dashboard.py` from `383` lines
  to `9` lines.
- [Coherence #85](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/85) (`4d2cfcf81`) extracted shared math
  into `metrics_math.py`, shrinking `src/holon_coherence/metrics/aggregation.py` from `222` lines to `150` lines.
- Both files are now below Coherence's `200`-line default cap, yet `holon-config/hygiene/module_budgets.json` still
  carries stale overrides (`"src/holon_coherence/proxy/dashboard.py": 383` and
  `"src/holon_coherence/metrics/aggregation.py": 222`), because `scripts/check_module_budgets.py` /
  `tests/test_module_budgets.py` only prints a `Ratchet notice:` on shrinking overrides and does not reject missing or
  stale override entries.

### Proposed Change

1. Update Coherence `scripts/check_module_budgets.py` (and `tests/test_module_budgets.py`) to fail when
   `holon-config/hygiene/module_budgets.json` references a non-existent file path and report/enforce pruning overrides
   whose line count is at or below `default_max_lines` (mirroring HAC Bean `0585`).
2. Under maintainer budget-change authorisation, prune the stale `dashboard.py` (`9/383L`) and `metrics/aggregation.py`
   (`150/222L`) overrides from `holon-config/hygiene/module_budgets.json`.

### Expected Gain & Cost

- Keeps `holon-config/hygiene/module_budgets.json` accurate and prevents shrunk modules from creeping back up to old
  limits (`383L` / `222L`).
- Cost: ~30 lines in `scripts/check_module_budgets.py` + `tests/test_module_budgets.py` + budget prune.

## Acceptance Criteria

- [ ] `scripts/check_module_budgets.py` fails immediately if `holon-config/hygiene/module_budgets.json` names a
      missing/deleted path and flags stale overrides at or below `default_max_lines`.
- [ ] Stale overrides for `src/holon_coherence/proxy/dashboard.py` and `src/holon_coherence/metrics/aggregation.py` are
      pruned from `holon-config/hygiene/module_budgets.json` under maintainer authorisation.
- [ ] `uv run pytest` and `uv run task lint` pass with zero docstrings or comments.

## Resolution
