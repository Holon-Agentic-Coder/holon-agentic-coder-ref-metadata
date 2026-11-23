---
# holon-agentic-coder-ref-metadata-0362
title: "Clear the stale-calibration warning when a fresh calibration lands"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - calibration
  - stage-5
  - github
  - holon-agentic-coder
created_at: 2026-11-23T03:20:00Z
updated_at: 2026-11-23T03:20:00Z
---

## Problem

`flow/calibrate_rerun.py` (around line 189) posts a PR comment headed "⚠️ Calibration report is stale" when
non-calibration commits land after the evaluated commit ("Stage 5 must rerun; do not merge on this report"). When Stage
5 then reruns and commits a fresh report covering the head, nothing clears, edits or supersedes that comment, so the PR
keeps telling the maintainer not to merge.

Seen on PR #243 (2026-11-23): warnings at 02:46:50 (report `8048484`, head `a8d0eae`) and 03:05:31 (report `8048484`,
head `58fe0be`). Stage 5 reran at 03:05:55 and the new report evaluated `25099f0a`, the last non-calibration commit, so
the merged report was current. Both warnings stayed on the PR and were the last word on it.

## Goal

- When a calibration report lands whose evaluated commit covers every non-calibration commit on the head, each earlier
  stale-calibration comment on the PR is resolved: edited in place (or minimised as outdated) to say it is superseded,
  naming the fresh report's evaluated SHA.
- A still-stale state keeps a single current warning (update the existing comment rather than adding another).
- Unit tests cover: warn → fresh calibration → warning marked superseded; warn → more commits → one updated warning; no
  warning when the report is current. Extend `tests/test_calibrate_rerun.py`.

## Notes

- Comment edits go through the existing GitHub posting path; keep a single place that owns the warning's lifecycle.
