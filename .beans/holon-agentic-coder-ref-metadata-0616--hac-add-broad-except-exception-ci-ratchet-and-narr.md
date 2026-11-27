---
# holon-agentic-coder-ref-metadata-0616
title: "HAC: add broad except-Exception CI ratchet and narrow non-boundary catches"
status: completed
type: task
priority: normal
tags:
  - holon-agentic-coder
  - resilience
  - ci
created_at: 2026-11-27T05:26:26Z
updated_at: 2026-11-27T23:48:13Z
---

## Notes

- **Problem**: Between `f006e79b` and `5c0a557cc`, broad `except Exception` handlers in `holon-agentic-coder` `src/`
  grew from `128` to `137` (`+9` in 42 PRs). While Bean `0534` addresses the 3 silent `except Exception: pass` sites and
  library `sys.exit(1)` calls, nothing prevents new non-boundary broad catches from accumulating.
- **Proposed Change**: Add a fast AST ratchet test in `holon-agentic-coder` CI capping `except Exception` counts per
  module/package (excluding explicit top-level CLI/stage fail-safe boundaries with `# why:` justification), and narrow
  non-boundary catches to specific exception classes (`OSError`, `subprocess.SubprocessError`, `json.JSONDecodeError`,
  `ValueError`, etc.).
- **Reference**: Source: 2026-11-27 ecosystem architecture audit (`docs/ecosystem-audit-report-2026-11.md`); complements
  Bean `0534`.
- **Progress (2026-11-27)**: [PR #414](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/414) (`2441e9d4`,
  `hac-broad-except-ratchet`) merged into `main`: added the fast AST ratchet test
  `apps/sandbox-executor/tests/test_broad_except_ratchet.py` locking per-module and per-package `except Exception`
  counts (Stage 4 approved and Stage 5 calibrated). Live `src/` `broad_except` dropped `138 -> 137` by `2a83e4cc7` (`3`
  silent `except Exception: pass` remain in `agent_runner.py:415`, `flow/pipeline.py:393`,
  `launcher/containers.py:209`). Keeping `status: in-progress` for the remaining slice to narrow non-boundary
  `except Exception` catches to typed exceptions.
- **Slice 2 (`hac-narrow-broad-excepts`)**:
  [PR #444](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/444) completed all 5 stages and is
  `MERGEABLE` / `CLEAN`, awaiting human maintainer merge.
  - Branch: `I-1795802426-hac-narrow-broad-excepts/P-1795802448-ANA-G4N/E-1795812780-ANA-G4N/_`
  - Worktree: `apps/holon-agentic-coder/flow-hac-narrow-broad-excepts`
  - Checkpoint:
    `apps/holon-agentic-coder/flow-hac-narrow-broad-excepts/.holon/flow/checkpoint-hac-narrow-broad-excepts.json`
  - Consensus: `APPROVED` (3/3 reviewers: 0/0/0)
  - CI: 16/16 checks passed (`0 cancelled, 0 failing, 16 successful, 0 skipped, 0 pending`)
  - Calibration: `plans/I-1795802426-hac-narrow-broad-excepts/P-1795802448-ANA-G4N_calibration.md` included in PR diff
    (Predicted EV `41.09`, Actual EV `50.45`, `ΔEV: +9.36`)

## Acceptance Criteria

- CI fails when unratcheted `except Exception` catches are added (ratchet-only cap per module/package passes when equal
  or lower).
- Non-boundary modules narrow catches to typed exceptions.

## Resolution

Delivered across two merged slices into `main`:

- **Slice 1 ([PR #414](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/414), `2441e9d4`)**: Added the
  AST broad-`except Exception` CI ratchet in `apps/sandbox-executor/tests/test_broad_except_ratchet.py`.
- **Slice 2 ([PR #444](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/444), `ec16d88c39`,
  `hac-narrow-broad-excepts`)**: Narrowed non-boundary catches in `attribution_check.py`, `calibration/physics.py`,
  `knowledge/consult.py`, `knowledge/promotion_rules.py`, and `knowledge/stats.py` to typed exceptions and tightened
  `test_broad_except_ratchet.py` with tests in `test_attribution_check.py`, `test_calibration_metrics.py`,
  `test_knowledge.py`, and `test_promotion_rules.py` (`16/16` CI checks `SUCCESS`).
- **Readiness (`pr_readiness.py --record`, PR #444)**: Head `ff231e28`, Consensus `APPROVED` (`7369f08b`), Stage 5
  calibration `calibrate=success` (`plans/I-1795802426-hac-narrow-broad-excepts/P-1795802448-ANA-G4N_calibration.md`),
  `gates: consensus=ok, calibration=ok, pipeline=ok`.
