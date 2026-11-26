---
# holon-agentic-coder-ref-metadata-0582
title: "Self-explaining gate: sweep open PR heads when the gate lands; measure by AST, not text"
status: todo
type: task
priority: normal
tags:
  - harness
  - invariants
  - flow
created_at: 2026-11-26T23:51:36Z
updated_at: 2026-11-26T23:51:36Z
---

## Evidence (measured with `gh pr diff`, added lines only)

- #357 (gate, merged 23:44:54Z): 22 added triple-quoted lines in 12 blocks, all in the gate's own test fixtures (data,
  not docstrings), so a text count overstates; an AST/tokenizer count is needed to judge.
- #358 (merged 23:23:01Z, before the gate was on main): added three real docstrings (conftest hook, test module, test
  helper; about 15 lines) and a `#:` comment. A flow in flight when the gate lands never meets it: the gate only reaches
  a branch after it merges main.
- #359 (merged 23:50:00Z, after the gate): 0 docstrings, 0 plain comments, 3 `# why:` comments. The gate held once it
  was on main.
- Invariant registry: `self-explaining-code` still `partial` (beans 0558, 0574).

## Change

- When a gate lands on main, the coordinator runs it over every open PR head's added lines and resumes the flows whose
  heads fail, before they merge; otherwise the gate has a blind window equal to every PR opened earlier.
- A small measuring script reports per PR: added docstring lines (via tokenize/AST), added non-`# why:` comments,
  fixture-string lines excluded; use it in readiness checks (CF-0012 rule) and audits.
- Open a flow to strip the three #358 docstrings and the comment.

## Expected gain

Closes the blind window (one merged PR with docstrings today) and gives audits real counts. Cost: small script plus one
cleanup flow.
