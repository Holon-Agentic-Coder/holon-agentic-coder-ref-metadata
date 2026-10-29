---
# holon-agentic-coder-ref-metadata-0211
title: "holon-coherence docs: A/B test recipe runs mitmdump in the foreground; metrics after a restart show one pass"
status: todo
type: bug
priority: low
tags:
  - holon-coherence
  - documentation
created_at: 2026-10-30T02:00:00Z
updated_at: 2026-10-30T02:00:00Z
---

## Problem

holon-coherence PR #31 (the post-merge follow-up to PR #29) was merged as `b52c7e1` while its iteration-19 ensemble (at
`52a843b`) still had two documentation Nits open:

- **C19-1:** the host-side `mitmdump` step of the A/B test recipe runs in the foreground, so the `ab-test --command`
  line after it never runs as written.
- **C19-2:** `metrics --json` after the proxy restart reports only the optimised pass, not both.

## Scope

- Fix both recipes (run `mitmdump` in the background or in a second terminal, and state how to keep both passes'
  metrics), checked against the real CLI behaviour.
- Documentation only; through the Holon flow on holon-coherence.

## Notes

- Related: Bean 0147 (holon-coherence half done via PRs #29 and #31).
