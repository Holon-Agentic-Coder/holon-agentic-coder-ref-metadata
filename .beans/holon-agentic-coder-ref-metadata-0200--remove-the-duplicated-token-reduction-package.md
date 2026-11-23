---
# holon-agentic-coder-ref-metadata-0200
title: "Remove holon-agentic-coder's diverged token_reduction copy; holon-coherence is the single owner"
status: completed
type: task
priority: normal
tags:
  - refactor
  - duplication
  - token-reduction
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0189
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-23T05:48:20Z
---

## Problem

Spawned by Bean 0177; this is Bean 0152 scope item 4. `sandbox_executor/token_reduction/` (`993b686`, 2,819 lines) is a
diverged copy of holon-coherence (`68fdf67`): `mitm_addon` 1,358 vs 2,348 lines (2,358 differing lines), `hybrid_cache`
308 vs 446, `payload_cleaner` 552 vs 598, `ca_generator` 251 vs 278. Both contain the same 192-line
`extract_sse_token_counts` (CC 85). Production code imports only `generate_root_ca` from it (`cli.py`); the rest is
reached only by tests (`test_token_reduction.py` 3,734 lines, `test_context_cleaner.py` and fuzz tests). The proxy that
actually runs is the holon-coherence image.

## Scope

1. **Decision first (recorded in this bean before Stage 1):** holon-coherence owns token reduction. Confirm in the plan
   that no image, Dockerfile, bake target or runtime path loads `sandbox_executor.token_reduction` other than CA
   generation.
2. Keep CA generation (move it next to the sidecar launcher from 0189, or call holon-coherence's `init-ca`).
3. Delete the remaining modules and their tests; move any test that guards holon-agentic-coder behaviour (redaction on
   URLs, sidecar env) to the module it tests.
4. No reduction in coverage of code that remains.

## Touch set

`sandbox_executor/token_reduction/`, `launcher/sidecar.py` (CA call), `tests/test_token_reduction.py`,
`tests/test_context_cleaner.py`, the fuzz tests' imports, `docs/` references.

## Dependencies

Blocked by 0189. **Maintainer decision (2026-10-29): token reduction is owned by holon-coherence.** holon-agentic-coder
keeps only what it needs to use holon-coherence (for example the root CA generation, sourced from holon-coherence) and
deletes its own copy. Related to 0157 (sidecar auto-enable).

## Notes

- Run through the Holon flow on holon-agentic-coder.
- A tracked `todo/ab_measure_all_methods.py` imports this package; it is a harness-path leak handled by Bean 0147.

## Audit (2026-11-21)

Still valid and still blocked by Bean 0189. Production code still imports `generate_root_ca`, `proxy_readiness` and
`PROXY_READY_TIMEOUT_SECONDS` from `sandbox_executor.token_reduction`, now in `cli/__init__.py` (the `cli.py` reference
above is stale); `token_reduction/` still holds the full diverged copy.

## Flow attempt (2026-11-23): not dispatched

Blocked by Bean 0189, which is still `todo` with no open PR. Scope item 2 and the touch set name `launcher/sidecar.py`,
a file 0189 creates; on `main` the CA import sits in `cli/__init__.py`. Token reduction is also imported beyond CA
generation (`flow/pipeline.py`, `cli/commands/*`, `cli/options.py`, and about 20 tests), so the Stage 2 plan would
collide with 0189's move. The bean stays `todo` until 0189 is completed, or the maintainer explicitly sequences this
ahead of it. No intent JSON was dispatched.

## Re-audit (2026-11-23, after Bean 0189 merged): blocked, not dispatched

Blocker 0189 is `completed` (PR #241 merged), so the dependency is cleared. The scope premise is not: origin/main still
runs the local addon at runtime.

- `launcher/sidecar_plan.py` (`_mitm_addon_path`) mounts `token_reduction/mitm_addon.py` into a
  `mitmproxy/mitmproxy:12.2.3` sidecar (`mitmdump -s /tmp/mitm_addon.py`). Deleting `token_reduction/` removes the addon
  that `--token-reduce` runs today.
- `launcher/sidecar.py` imports `proxy_readiness` and `PROXY_READY_TIMEOUT_SECONDS` from the package; `cli/__init__.py`
  re-exports them. These need re-homing, not deletion.
- Code outside CA generation imports the package in about 25 places (`cli/options.py`,
  `cli/commands/{execute,intent,plan}.py`, `flow/pipeline.py`, `launcher/{containers,proxy_attach}.py`,
  `scripts/ab_measure_all_methods.py`, and tests).
- holon-coherence already ships its own addon (`src/holon_coherence/proxy/addon.py`, `mitm_addon.py`) and a proxy
  `Dockerfile`. The bean's "holon-coherence owns token reduction" decision therefore implies repointing the sidecar to
  that image and addon. The bean does not specify this, and it is a design change.

Decision needed from the maintainer before a flow can be scoped:

1. Repoint the sidecar to the holon-coherence image and addon (contract, image name, mounts, and whether
   holon-agentic-coder requires it to be present), then delete `token_reduction/`; or
2. Keep the local addon for now, and narrow this bean to deleting the unused modules and tests (`rag_indexer`,
   `ringer_orchestrator`, `openbrain_memory`) with their tests.

Status stays `todo`: no flow was started, no intent was written to `todo/`, and no worktree or PR exists for this bean.

## Maintainer decision (2026-11-23)

Full removal. Repoint the token-reduce sidecar to holon-coherence's own proxy addon and image
(`src/holon_coherence/proxy/addon.py` and its proxy `Dockerfile`), re-home `proxy_readiness` and every other remaining
reference, then delete `token_reduction/` and its tests entirely.

## Resolution

Delivered via [PR #249](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/249) and merged into `main`
(`c905a98`), with full removal per the maintainer decision of 2026-11-23:

- **Key Architectural Deliverables**: `sandbox_executor/token_reduction/` deleted (including the diverged
  `mitm_addon.py`, `hybrid_cache`, `payload_cleaner`, `rag_indexer`, `ringer_orchestrator`, `openbrain_memory`). Root CA
  generation moved to `launcher/root_ca.py` and `launcher/root_ca_openssl.py`; `proxy_readiness` re-homed to
  `launcher/`; the token-reduce sidecar now uses the holon-coherence proxy image and addon via `launcher/proxy_image.py`
  and `launcher/sidecar*.py`. Related token-scope and execution-recovery modules added under `flow/`.
- **Verification & Tests**: `test_token_reduction.py` and `test_context_cleaner.py`, `test_cache_control.py` removed
  with their modules; replacement launcher, sidecar, root-CA, proxy-env, token-scope and execution-recovery tests added;
  the URL fuzz test repointed to the moved modules.
- **Holon Flow Traversal**: Intent, plan (`P-1795409242-CLA-CO5.5`) and execute (`E-1795409573-CLA-CO5.5`) completed and
  merged after review; calibration recorded in
  `plans/I-1795409225-remove-token-reduction-copy/P-1795409242-CLA-CO5.5_calibration.md` (EV predicted 30.15; clean
  actual 58.99; observed -21.01 with bug EV drag 80).
