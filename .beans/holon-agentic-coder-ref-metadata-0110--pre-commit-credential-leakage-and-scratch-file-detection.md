---
# holon-agentic-coder-ref-metadata-0110
title: "Implement pre-commit credential leakage and ephemeral scratch file detection"
status: todo
type: task
priority: normal
tags:
  - security
  - pre-commit
  - git-hooks
  - credentials
  - hygiene
created_at: 2026-10-17T04:15:30Z
updated_at: 2026-10-17T04:15:30Z
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

- [ ] Define credential scanning patterns (Google AI `AIza[0-9A-Za-z\-_]{30,40}`, GitHub PATs `ghp_...`, OpenAI
      `sk-...`) in a reusable git pre-commit hook script.
- [ ] Add checks preventing staging of disallowed paths (`tmp/*`, `*.tmp`, `*.log`, `.index/*`).
- [ ] Ensure the pre-commit hook runs quickly and outputs clear error diagnostics pointing to offending lines.
- [ ] Document the hook setup in `.agents/rules.md` and repository README.
- [ ] Verify test suite with mock files and secret strings.
