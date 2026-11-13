---
# holon-agentic-coder-ref-metadata-0281
title: "Carry the calibration report that missed its PR into `main` in one pull request"
status: in-progress
type: task
priority: normal
tags:
  - calibration
  - flow
  - holon-agentic-coder
created_at: 2026-11-12T10:00:00Z
updated_at: 2026-11-12T10:00:00Z
---

## Problem

The first Bean 0262 flow (PR #159) produced a Stage 5 calibration report on its `calibrated` branch, but PR #159 was
reverted (#160) and the re-land (#162) was hand-assembled, so the report never reached `main`. A survey of every
`calibrated` branch left on `origin` after the 2026-11-12 branch clean-up found this is the only one whose report is
missing from `main`:

- `plans/P-1794268104-fd29467b-antigravity-agent-gemini-3.8-flash-medium_calibration.md`, branch
  `I-1794268087-mount-host-worktree-into-sandbox-containers/P-1794268104-fd29467b-antigravity-agent-gemini-3.8-flash-medium/E-1794270142-ea5a02bf-antigravity-agent-gemini-3.8-flash-high/calibrated`
  (commits `2e63f36` the report plus its ledger rows, and `26d7b9a` the stage-5 reconciliation row).

Older plans without a report in `main` have no `calibrated` branch left, so they cannot be recovered this way (see Bean
0268).

## Action

One branch off `origin/main` carrying the two calibration commits by `cherry-pick -x`, ledger-only conflicts resolved by
interleaving rows on `created_at` and removing duplicates, one pull request into `main` for the maintainer.

**Exception to the sole-change-path rule:** assembled by hand outside the Holon flow, at the maintainer's explicit
instruction (2026-11-12). It moves existing, flow-generated, already-audited artefacts and authors no new code. The
exception is named in the commit messages.

## Follow-up

Do not delete the `I-1794268087-...` branch tree until this pull request has merged.
