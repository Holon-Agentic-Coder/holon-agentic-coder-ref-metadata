---
# holon-agentic-coder-ref-metadata-0110
title: "Implement pre-commit credential leakage and ephemeral scratch file detection"
status: completed
type: task
priority: normal
tags:
  - security
  - pre-commit
  - git-hooks
  - credentials
  - hygiene
created_at: 2026-10-17T04:15:30Z
updated_at: 2026-10-18T09:40:00Z
---

Implement automated pre-commit and pre-push hooks to intercept API keys, credentials, and ephemeral scratch files before
they can be staged or pushed.

## Context

- In recent PR review cycles (e.g. PR #78 review findings 1 and 3), accidental scratch files (such as
  `tmp/test_write.txt` and unstaged index files) and credential regex edge cases were caught during downstream review
  passes.
- Catching secret patterns (Google AI API keys `AIza...`, GitHub personal access tokens, OpenAI keys) and untracked
  transient scratch artifacts locally at the pre-commit boundary prevents accidental leakage to remote branches and
  avoids consuming review loop iterations on basic hygiene oversights.

## Tasks

- [x] Define credential scanning patterns (Google AI `AIza[0-9A-Za-z\-_]{30,40}`, GitHub PATs `ghp_...`, OpenAI
      `sk-...`) in a reusable git pre-commit hook script.
- [x] Add checks preventing staging of disallowed paths (`tmp/*`, `*.tmp`, `*.log`, `.index/*`).
- [x] Ensure the pre-commit hook runs quickly and outputs clear error diagnostics pointing to offending lines.
- [x] Document the hook setup in `.agents/rules.md` and repository README.
- [x] Verify test suite with mock files and secret strings.

## Resolution Summary

Implemented `scripts/pre_commit_check.py` across both `holon-agentic-coder` (PR #84) and `holon-coherence` (PR #25) with
secret scanning (Google AI, GitHub PAT classic/fine-grained, OpenAI, Anthropic), disallowed ephemeral path detection
(`tmp/*`, `*.tmp`, `*.log`, `.index/*`), path normalisation preserving leading dots, unit tests, and integration into
`make pre-commit-check` and `make check`.
