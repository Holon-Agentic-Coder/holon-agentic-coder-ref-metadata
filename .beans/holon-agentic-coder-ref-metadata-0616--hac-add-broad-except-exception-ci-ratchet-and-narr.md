---
# holon-agentic-coder-ref-metadata-0616
title: "HAC: add broad except-Exception CI ratchet and narrow non-boundary catches"
status: in-progress
type: task
priority: normal
tags:
  - holon-agentic-coder
  - resilience
  - ci
created_at: 2026-11-27T05:26:26Z
updated_at: 2026-11-27T11:55:26Z
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

## Acceptance Criteria

- CI fails when unratcheted `except Exception` catches are added (ratchet-only cap per module/package passes when equal
  or lower).
- Non-boundary modules narrow catches to typed exceptions.

## Resolution
