---
# holon-agentic-coder-ref-metadata-0299
title: "Stage 5 calibrate no longer fails with git diff 'ambiguous argument' on nested sub-intent branch names"
status: in-progress
type: bug
priority: high
tags:
  - stage-5
  - calibration
  - decomposition
  - holon-agentic-coder
created_at: 2026-11-14T10:30:00Z
updated_at: 2026-11-14T10:30:00Z
---

## Problem

On the touchset flow (a decomposed intent), Stage 5 failed with `git diff` exit 128, "ambiguous argument", on the nested
sub-intent branch names, so no calibration report was committed or pushed. The branch names contain slashes and a `/_`
suffix; the diff arguments are probably ambiguous between a ref and a path (no `--` separator, or a short name that
resolves to more than one ref).

## Scope

1. Reproduce from the touchset flow worktree's checkpoint and find the failing `git diff` call in the calibrate path.
2. Fix it by passing fully qualified refs and a `--` path separator; sweep the other Stage 5 and calibrate-sync git
   calls for the same pattern.
3. Hermetic tests using a nested sub-intent branch layout that reproduces the failure.

## Notes

Run through the Holon flow on holon-agentic-coder. Disjoint from Bean 0298. A calibrate rerun on the touchset flow
depends on it.
