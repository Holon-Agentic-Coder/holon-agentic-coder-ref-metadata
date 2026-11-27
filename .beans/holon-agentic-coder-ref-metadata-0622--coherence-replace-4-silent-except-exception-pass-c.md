---
# holon-agentic-coder-ref-metadata-0622
title: "Coherence: replace 4 silent except-Exception-pass catches and ratchet broad catches"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - resilience
  - error-handling
  - ci
created_at: 2026-11-27T08:03:26Z
updated_at: 2026-11-27T10:56:02Z
---

## Notes

- **Problem**: `holon-coherence@ce39bf34d` has `34` broad `except Exception` handlers in `src/` (`36` including
  `scripts/`), including **4 silent `except Exception: pass` blocks** not covered by Bean `0529`:
  - `src/holon_coherence/commands/ca.py:40` (TLS verification path lookup)
  - `src/holon_coherence/commands/docker_ops.py:81` (container port parsing)
  - `src/holon_coherence/commands/docker_ops.py:169` (post-run metrics summary printing)
  - `src/holon_coherence/proxy/wire_log.py:69` (wire-log mode parsing)
- **Audit update (`2026-11-27T10:55Z`, `52019174f`):** PR `#69` (`2659364`) resolved
  `src/holon_coherence/proxy/wire_log.py:69`, reducing silent `except Exception: pass` blocks to **3**
  (`commands/ca.py:40`, `commands/docker_ops.py:81,169`) and `broad_except` in `src/` from `34` to **`33`** (`35`
  including `scripts/`).
- **Proposed Change**: Replace all 4 silent `except Exception: pass` blocks with narrowed exception types (`OSError`,
  `ValueError`, `json.JSONDecodeError`, `subprocess.SubprocessError`) and explicit debug/warning logging, and add an AST
  CI ratchet capping `except Exception` counts per module (mirroring HAC Bean `0616`).
- **Expected Gain & Cost**: Eliminates silent failure swallowing in CLI/proxy utilities and prevents broad-catch creep;
  small targeted cleanup + AST test.
- **Reference**: Source: 2026-11-27 architecture & code-quality refresh (`docs/ecosystem-audit-report-2026-11.md`);
  complements Bean `0529` and mirrors HAC Beans `0534` / `0616`.

## Acceptance

- Zero silent `except Exception: pass` blocks remain in `holon-coherence/src/`.
- CI fails if unratcheted `except Exception` catches are added outside explicit proxy/CLI boundary handlers.

## Resolution
