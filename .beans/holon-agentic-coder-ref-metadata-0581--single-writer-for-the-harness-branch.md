---
# holon-agentic-coder-ref-metadata-0581
title: "Single writer for the shared harness branch: per-agent paths or a serialised commit step"
status: todo
type: task
priority: high
tags:
  - harness
  - git
  - coordination
created_at: 2026-11-26T23:51:36Z
updated_at: 2026-11-26T23:51:36Z
---

## Evidence

- CF-0010 (`git add -A` swept another agent's bean), CF-0015 (hook failed on another agent's file, `--no-verify` used),
  CF-0022 (coordinator edited a ledger file another agent had staged; wrong content committed).
- At audit start the shared tree held uncommitted edits from at least three agents (beans 0489, 0558, 0563, 0564, 0572,
  0574 modified) on `docs/harness-20261127`; one agent's bad file blocks every other agent's commit (0577 second
  symptom). Bean 0577 fixes what the hook validates; it does not fix several agents sharing one index.

## Change

- One harness commit path: `.agents/scripts/harness_commit.py <message> <paths...>` takes a lock (`flock` on
  `.git/harness-commit.lock`), refuses paths with a staged diff that differs from the working copy, stages only the
  named paths, commits, releases. Refuses an empty path list.
- Agents write files in the shared tree but only commit through it; coordinator checks `git diff --cached` is empty
  before editing a shared file (CF-0022 rule becomes tooling).
- Test: two concurrent invocations serialise; a mismatched staged file is refused.

## Expected gain

Ends cross-agent sweeps and the temptation to bypass hooks. Cost: one script, tests. Complements 0577 and 0578.
