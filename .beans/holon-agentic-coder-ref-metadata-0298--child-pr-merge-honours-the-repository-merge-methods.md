---
# holon-agentic-coder-ref-metadata-0298
title: "Child PR merge into the plan branch honours the repository's allowed merge methods"
status: completed
type: bug
priority: high
tags:
  - holon-flow
  - merge
  - decomposition
  - holon-agentic-coder
created_at: 2026-11-14T10:30:00Z
updated_at: 2026-11-14T12:33:40Z
---

## Problem

`flow/github/merge.py` always runs `gh pr merge <n> --merge --match-head-commit <sha>`. The target repository allows
squash merges only (`allow_merge_commit: false`), so GitHub rejects the merge ("Merge commits are not allowed on this
repository") and a decomposed flow stops at Stage 3. Seen on the touchset flow (PR #194, 2026-11-14); the maintainer
merged the child PR by hand.

## Scope

1. Read the repository's allowed merge methods (`gh api repos/{owner}/{repo}`) and use the merge commit when allowed,
   otherwise squash, never rebase, `--auto`, `--admin` or `--delete-branch`. The `main`/default-branch refusal and the
   `--match-head-commit` guard stay unchanged and fail closed.
2. Update the module docstring and any document that says "merge commit only".
3. Hermetic tests with an injected `gh` runner: merge allowed, squash-only, neither allowed (refuse), lookup failure
   (refuse), `main` still refused.

## Notes

Run through the Holon flow on holon-agentic-coder. Disjoint from Bean 0299.

## Resolution

Delivered via [PR #196](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/196) and merged into `main`
(`721cd36`):

- **Key Architectural Deliverables**: `flow/github/merge.py` reads the repository's allowed merge methods and uses a
  merge commit when allowed, otherwise a squash when merge commits are disallowed. It never rebases and never uses
  `--auto`, `--admin` or `--delete-branch`. The `main`/default-branch refusal and the `--match-head-commit` guard are
  unchanged and still fail closed. The module docstring and the flow documents no longer say "merge commit only".
- **Verification & Tests**: hermetic tests with an injected `gh` runner cover merge allowed, squash-only, neither
  allowed (refuse), lookup failure (refuse) and `main` still refused.
- **Holon Flow Traversal**: all 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed. The review
  reached 3/3 consensus. EV predicted 56.55, actual 69.22.
- **Post-merge**: `holon` reinstalled from `main` at `721cd36` (`holon --version` reports 0.1.0). Bean 0299 (PR #197)
  and Bean 0151 remain in progress.
