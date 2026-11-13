---
# holon-agentic-coder-ref-metadata-0277
title: "Flow executor commits carry a `Co-Authored-By` attribution trailer"
status: completed
type: bug
priority: normal
tags:
  - flow
  - executor
  - attribution
  - holon-agentic-coder
created_at: 2026-11-12T09:00:00Z
updated_at: 2026-11-12T09:00:00Z
---

## Problem

The executor container runs Claude Code, whose default attribution adds
`Co-Authored-By: Claude <model> <noreply@anthropic.com>` to the commits the agent makes. The maintainer's rule is that
no commit carries an attribution trailer. Seen on 2026-11-11: PR #164's first commit (`4879664`) and two commits in PR
#163 carry the trailer; PR #165 and #166 had none, so it depends on the agent's own commit.

## Action

Run through the Holon flow. Start the container's Claude Code with attribution disabled (the `includeCoAuthoredBy` /
attribution setting, passed through the existing settings route, not a bypass of permissions), and add a Stage 3 check
that fails or rewrites nothing but reports any attribution trailer found in the execution branch's own commits. Hermetic
tests only. Flow branch history is never rewritten after the fact, so this only prevents new trailers.

## Resolution (completed, 2026-11-13)

Delivered by flow `attrib` as holon-agentic-coder PR #183, merged 2026-11-13T01:06:20Z (merge commit `9852861`, review
`PRR_kwDORMmd1c8AAAABXrx9jA`). Calibration report
`plans/P-1794529179-a03ed51a-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
+10.92 (actual 46.47). The PR needed a conflict merge with `origin/main` after PR #182 landed, resolved by the
`resolve-conflict` skill on the lowest model tier.
