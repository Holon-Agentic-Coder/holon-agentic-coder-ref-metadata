---
# holon-agentic-coder-ref-metadata-0608
title: "Reason comments deleted by 0153 slices are never restored as why comments"
status: todo
type: bug
priority: high
tags:
  - self-explaining-code
  - holon-flow
created_at: 2026-11-27T04:43:38Z
updated_at: 2026-11-27T04:43:38Z
---

## Evidence (audit 2026-11-27T04:43Z, PRs #396, #393, #392, #390, #389, #385, #384, #382, #383, #380)

- Removed comment lines that read as reasons (keywords because, so that, otherwise, must, avoid, never, race, ensure) in
  the nine slice diffs: 10, 2, 4, 88, 16, 2, 19, 1, 6, about 148 lines. A heuristic; none of the PR bodies reports how
  many reasons were deleted, so the true count is **not measured**.
- `# why:` lines added: 37, 23, 37, 242, 62, 8, 98, 8, 40; no `# why:` line removed. Added counts include docstring
  reasons, so they do not show which deleted reasons survived.
- Bean 0153 already records deletions per slice (9 in one slice, "Lazy:" import reasons dropped in #401) but no restore
  slice or bean exists: grep of beans for restore finds nothing.

## Goal

1. Measure: a script compares removed comment text against added `# why:` text per merged slice and lists removed
   reasons with no counterpart (file, line, text).
2. Restore: one flow intent per package re-adds the lost reasons as `# why:` where the code cannot show them.
3. Prevent: the 0153 intent template tells the planner to keep each reason as `# why:` and the PR body to report reasons
   kept and deleted.

## Acceptance

- [ ] The list of unmatched removed reasons exists for every merged 0153 slice.
- [ ] Each entry is restored or marked as shown by the code, with the reason.
- [ ] New slice PR bodies report reasons kept and deleted.

## Notes

## Resolution
