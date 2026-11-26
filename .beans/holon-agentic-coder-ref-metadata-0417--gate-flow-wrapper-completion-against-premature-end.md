---
# holon-agentic-coder-ref-metadata-0417
title: "Gate flow wrapper completion against premature end"
status: completed
type: bug
priority: high
tags:
  - harness
  - holon-flow
  - reliability
created_at: 2026-11-24T11:05:00Z
updated_at: 2026-11-25T05:30:00Z
---

## Why

`run_holon_flow.py` ends a flow without checking that the flow delivered what it promised, and the state file that a
resuming agent reads is left to the driving subagent's prose. A flow can therefore be reported finished while it has no
pull request, no calibration report or a conflicting pull request.

## Evidence

Reconstructed on 2026-11-24 from the self-improvement audit of 11:05Z, which names this bean as "Make
`run_holon_flow.py`'s `verify_pr_and_calibration` fail non-zero on missing PR/calibration/conflicting PR and write
`.subagent/flow_<slug>_state.json` deterministically instead of trusting `flash_lite` prose". The file's first version
was a copy of Bean 0416 and carried none of this text.

- `.agents/skills/holon_flow/scripts/run_holon_flow.py`, `verify_pr_and_calibration`: when no open pull request matches
  the slug it only calls `log_warn("No open PR found ...")` and returns, and a GitHub query failure is also only a
  warning. The wrapper then exits 0.
- The same function checks the calibration report in the pull request diff, but a missing report does not change the
  exit code, and a conflicting pull request is only logged with `log_error`, so the exit code is unchanged.
- The `.subagent/flow_<slug>_state.json` files are written by the driving subagent, not by the wrapper.

## Proposed change

1. `verify_pr_and_calibration` returns a result and the wrapper exits non-zero when there is no pull request for the
   slug, when the calibration report is absent from the pull request diff, or when the pull request is conflicting or
   not mergeable. A merged pull request (Bean 0420) is a clean finish.
2. The wrapper writes `.subagent/flow_<slug>_state.json` itself, deterministically, with the outcome and the pull
   request number, so a replacement driver does not depend on a model's summary.
3. Tests in `tests/test_flow_fallback.py` or a new test file cover each failing case.

## Notes

- Related: Bean 0420 (a flow whose pull request merges while running), Bean 0396 (a flow survives its session), Bean
  0416 (same wrapper script, different defect).
- Harness-only change; no target repository is touched.

## Resolution

`verify_pr_and_calibration` now returns a result (ok, problems, pr, calibration, mergeable, merge state, checks) and
`run_flow` exits 1 when the flow exits 0 but the PR is missing or unqueryable, closed unmerged, lacks the calibration
report in its diff, or is CONFLICTING/DIRTY; a merged PR is a clean finish. Pending checks are waited for (bounded 45
min, 30 s poll, via `gh pr checks`) and still-pending at the bound fails. The wrapper writes
`.subagent/flow_<slug>_state.json` itself (status, PR number/url, stage reached, consensus, calibration EV when logged,
merge state, next action). Dry runs are unchanged. Tests (fakes only, no gh) in `tests/test_flow_completion.py`. Full
suite: 179 passed.
