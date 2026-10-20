---
# holon-agentic-coder-ref-metadata-0125
title: "Enforce Australian English spelling across code comments and logging messages"
status: completed
type: task
priority: normal
tags:
  - style
  - clean-code
  - spelling
  - en-au
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T04:40:00Z
---

Audit and enforce Australian English (`en-AU`) orthography across all source code docstrings, comments, log strings, and
CLI outputs across the Holon ecosystem, while strictly preserving upstream licenses and legal text word-for-word.

## Context

Audit finding `AUD-2026-03`: While repository conventions mandate Australian English (`-ise` / `-our`), scattered
instances of American spelling (`initialize`, `behavior`, `optimize`, `serialize`) persist across `sandbox-executor` and
`holon-coherence`.

> [!IMPORTANT] **License Invariant**: All `LICENSE` files, license headers, and verbatim upstream legal text (e.g.
> Apache License, Version 2.0) **MUST remain word-for-word exact as the original upstream license** and **MUST NOT** be
> modified or converted to Australian English. Legal integrity takes strict precedence over orthographic
> standardization.

## Tasks

- [x] Run automated wordlist scan for US spelling variants across Python and shell code.
- [x] Exclude all `LICENSE` files, third-party vendor licenses, and upstream legal boilerplate from modification.
- [x] Replace identified occurrences in code comments, docstrings, and log strings with standard Australian English
      equivalents (`initialise`, `behaviour`, `optimise`, `serialise`, `prioritise`).
- [x] Add lint or regex hygiene check to prevent reintroduction of non-conforming spellings while maintaining license
      file exclusions.

## Resolution

- Replaced US spelling variants (`initialize`, `optimize`, `sanitize`, `serialize`, `prioritize`) with standard
  Australian English equivalents (`initialise`, `optimise`, `sanitise`, `serialise`, `prioritise`) across `flow.py`,
  `cli.py`, `scaffold.py`, `planner.py`, `executor.py`, and `payload_cleaner.py`.
- Added Australian English regex hygiene check `check_spelling_orthography` with `US_SPELLING_VARIANTS` and
  `SPELLING_EXEMPT_PATTERNS` to `scripts/pre_commit_check.py`, strictly preserving all `LICENSE*` files, third-party
  licenses, and upstream boilerplate word-for-word per the License Invariant.
- Added unit tests in `apps/sandbox-executor/tests/test_pre_commit_check.py` covering orthography detection and
  verifying license file preservation.
- Executed through full 5-stage Holon flow via PR #86:
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/86
