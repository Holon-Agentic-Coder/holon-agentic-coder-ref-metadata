---
# holon-agentic-coder-ref-metadata-0252
title: "Stage 4 resolver preserves its rejected diff and full test output when pre-push tests fail"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - stage-4
  - resolver
  - observability
  - holon-agentic-coder
created_at: 2026-11-09T00:30:00Z
updated_at: 2026-11-09T00:30:00Z
---

## Problem

During the PR #143 flow (Bean 0241), the native Stage 4 resolver on `claude-agent` / `claude-opus-5-5` failed its
pre-push test run on review iterations 5 and 6, each time with the same cluster of pytest setup errors (`E`) at 34–43%
of the 3,080-test suite. The loop halted both times with:

```text
[Review Loop] Halting review loop at iteration 5: Resolver pre-push test failed (exit code 1): ===== test session starts =====
```

The root cause could not be diagnosed because:

1. **The rejected change is discarded.** The resolver's working tree dies with the review-loop container, so the diff
   that broke the tests is never committed, pushed, or written anywhere the host can read.
2. **The test output is truncated.** The `error` string recorded in the review result and the flow log is cut off at
   roughly 2 KB, partway through the progress dots. The `short test summary info` section, which names the erroring
   tests and their exceptions, is lost.

Running the suite on the unchanged PR head showed no setup errors (3,094 passed, 1 host-specific failure), which proves
the resolver's own change caused them. But without the diff or the summary there was nothing to act on, and the only way
forward was to switch runner (to `antigravity-agent` / `gemini-3.8-flash-medium`) and hope a different model would not
make the same change.

## Goal

1. **Preserve the rejected diff**: When the resolver's pre-push test run fails, save its uncommitted changes as a patch
   (e.g. `git diff HEAD`) to a host-readable artefact under `.holon/` and record its path in the iteration's
   `executions.jsonl` action entry.
2. **Keep the test summary**: Record the tail of the pytest output, including the `short test summary info` section and
   the final counts line, rather than a head-truncated prefix. Keep the head truncation limit, but take it from the end
   of the output, or extract the summary section explicitly.
3. **Feed it back**: Give the next resolver pass the failing tests and the rejected diff, so it can avoid repeating the
   same breaking change.
4. **Redaction**: Run all saved output and patches through `redact_agent_secrets()`.
5. **Tests**: Add hermetic tests asserting that a failed pre-push run yields a saved patch, a recorded summary that
   names the failing tests, and a ledger entry pointing at both.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- Related: Bean 0250 (surface agent returncode and stderr in `review_ensemble.py`) made the reviewer-crash case
  diagnosable; this covers the resolver's test-failure case.
