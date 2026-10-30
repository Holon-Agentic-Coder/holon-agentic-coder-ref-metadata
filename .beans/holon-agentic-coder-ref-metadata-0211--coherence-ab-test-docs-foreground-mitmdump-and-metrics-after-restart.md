---
# holon-agentic-coder-ref-metadata-0211
title: "holon-coherence docs: A/B test recipe runs mitmdump in the foreground; metrics after a restart show one pass"
status: todo
type: bug
priority: low
tags:
  - holon-coherence
  - documentation
created_at: 2026-10-29T23:43:35Z
updated_at: 2026-10-30T00:59:03Z
---

## Problem

holon-coherence PR #31 (the post-merge follow-up to PR #29) was merged as `b52c7e1` (2026-10-29T23:24:46Z) with two
documentation Nits open. Its iteration-19 consensus review `5699924689` (state `COMMENTED`, submitted
2026-10-29T15:00:52Z, head `52a843b`) had been posted as a unanimous 3/3 `APPROVED` with 0 open findings. The
iteration-19 ensemble was then resumed after an API session limit, and its consensus, which closed after the merge at
the same head `52a843b`, found two documentation Nits that were never posted:

- **C19-1:** the host-side `mitmdump` step of the A/B test recipe runs in the foreground, so the `ab-test --command`
  line after it never runs as written.
- **C19-2:** `metrics --json` after the proxy restart reports only the optimised pass, not both.

## Scope

- Fix both recipes (run `mitmdump` in the background or in a second terminal, and state how to keep both passes'
  metrics), checked against the real CLI behaviour.
- Documentation only; through the Holon flow on holon-coherence.

## Notes

- Related: Bean 0147 (holon-coherence half done via PRs #29 and #31).
- **Correction (2026-10-30, checked against GitHub):** the Problem section first said PR #31 merged "while its
  iteration-19 ensemble (at `52a843b`) still had two documentation Nits open", without recording that review
  `5699924689` had already posted a 3/3 approval. That wording is superseded by the Problem section above.
