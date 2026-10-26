---
# holon-agentic-coder-ref-metadata-0154
title: "Fix flaky URL fuzz leak check that can match random temp-file names"
status: todo
type: bug
priority: normal
tags:
  - tests
  - flaky
  - redaction
  - holon-agentic-coder
created_at: 2026-10-25T08:01:22Z
updated_at: 2026-10-25T08:01:22Z
---

## Problem

On `main` (added by PR #96), `tests/test_url_message_fuzz.py`'s password-delimiter test fails intermittently inside the
sandbox-simulation path. The PR #94 sync resolver hit one failure in a full run on 2026-10-25. Sixty reruns and two
further full runs all passed.

The likely cause is that the leak check flags any fragment of the fake password of 4 or more characters that appears in
the captured output. The docker command line includes a randomly named env-file path (`tempfile`). When that random name
happens to share a 4-character run with the fake password, the check reports a leak that isn't one.

## Scope

- Reproduce deterministically by seeding the temp-file name or the fake value so they collide, and confirm this is the
  cause.
- Make the check exact. Either generate fake secrets from an alphabet or marker that temp names can't contain, or strip
  or allowlist the env-file path before matching, or match longer or whole tokens. It must still catch genuine partial
  leaks.
- Run the fuzz module many times in CI-like conditions (for example 200 iterations) to show the flake is gone.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Found by the PR #94 iteration-15 sync resolver (merge of #95).

## Resolution
