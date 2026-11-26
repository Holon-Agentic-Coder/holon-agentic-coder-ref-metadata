---
# holon-agentic-coder-ref-metadata-0452
title: "Stage 5 KB promotion persists single-flow Stage 4 review chatter as permanent KB-failure entries"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - stage-5
  - knowledge
  - kb-bloat
  - merge-conflicts
  - holon-agentic-coder
created_at: 2026-11-25T05:41:00Z
updated_at: 2026-11-25T05:41:00Z
---

# Stage 5 KB promotion persists single-flow Stage 4 review chatter as permanent `KB-failure` entries

## Summary

Stage 5 calibration (`knowledge/wisdom.py:263-311`) promotes `action_signatures` whenever
`(success_count + failure_count) >= 2` and `failure_ladder_state in ("repeated", "proven-fail")`. Because `target`
embeds each flow's unique branch (`I-.../P-.../E-.../_`) and Stage 4 emits multiple `ACT-FIND` / `ACT-REV` ledger rows
per PR, normal intra-PR review iterations trip `min_trials = 2` within minutes and write dozens of per-flow review
findings permanently into `holon-knowledge/kb/failure_modes/KB-failure-*.json` as `"status": "active"` / `"veto"`.

## Evidence

- **Repository inspection on `holon-agentic-coder` `main` (`2026-11-25T05:35Z`):**
  - `holon-knowledge/kb/failure_modes/` contains **`3,205` `KB-failure-*.json` files**.
  - **`2,896 / 3,205` (`90.4%`)** carry `evidence.ledger_refs` (`ACT-*`) spanning `< 3,600 s` (`2,868` fall inside a
    single 1-hour epoch bucket), proving they came from one flow's own run rather than repeated cross-flow failures.
  - Across recent `holon-agentic-coder` PRs, Stage 5 committed **`21`** new `KB-failure-*.json` files in `PR #296`
    (`split-cli-init-modules`), **`4`** in `PR #297` (`claude-auth-self-doc`), **`3`** in `PR #300`
    (`decomposition-rule-self-doc`), and **`6`** staged on live `PR #308` (`workspace-survival-job-parallel`).
  - Concrete samples on `main`:
    - `KB-failure-03b08676.json` (`#296`):
      `ledger_refs: ["ACT-FIND-1795564818-3a3c1d9f", "ACT-FIND-1795564661-45b31aab"]` (`157 s` apart in one PR),
      `failure_count: 2`,
      `payload.name: "Failure mode in I-1795523046-split-cli-init-modules/P-1795563158-ANA-G4N/E-1795563737-ANA-G4N/_"`.
    - `KB-failure-39fb567e.json` and `KB-failure-a26f5682.json` (`#300`): `ACT-REV-*` / `REV-*` (`2–5 s` apart in one
      PR), `failure_count: 3`, `"ladder_state": "proven-fail"`.
- **Root cause (`apps/sandbox-executor/src/sandbox_executor/knowledge/`):**
  - `wisdom.py:278-296` queries `action_signatures` with `WHERE (success_count + failure_count) >= ?` (`min_trials=2`)
    and persists `_promote_failure_candidate` (`wisdom.py:160-191`) regardless of origin or distinct intent count.
  - `promotion.py:32-47` (`compute_context_fingerprint`) and `ledger_sync.py:33-40` (`_derive_context_fingerprint`) hash
    raw flow/execution branch strings into `target`, so intra-flow reviewer/finding rows immediately self-collide into
    permanent KB vetoes.

## Proposed Change

1. Exclude intra-flow Stage 4 review/finding rows (`ACT-REV`, `ACT-FIND`) from global `KB-failure-*.json` promotion — or
   require failure evidence from **`>= 2` distinct intents** (`intent_id` / normalized non-flow `target`) before
   promoting a failure mode or veto.
2. Add unit tests verifying multiple `ACT-FIND`/`ACT-REV` rows within one flow (`I-...`) do not produce a
   `KB-failure-*.json` artifact, while recurring failures across separate flows still promote cleanly.
3. Follow up separately to prune/archive existing single-flow Stage 4 `KB-failure-*.json` clutter (`2,896+` files
   checked on every CI `make lint-json` run).

## Expected gain

Stops every multi-reviewer / multi-iteration PR from committing `3–21` spurious `KB-failure-*.json` files into git,
shrinks `holon-knowledge/kb/failure_modes/` (`3,205` JSON files scanned by CI hygiene), removes `KB-failure-*.json`
add/add conflicts across parallel PRs, and restores signal to the failure-mode KB.

## Cost

Small-to-medium: promotion filter and target normalization in `knowledge/wisdom.py` / `knowledge/ledger_sync.py` + unit
tests, delivered via `holon flow` (`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0371` (per-flow pending ledger fragments and KB conflict reduction).
- Audit source: `2026-11-25T05:41Z` fifth-merge self-improvement audit (`#295–#299`).
