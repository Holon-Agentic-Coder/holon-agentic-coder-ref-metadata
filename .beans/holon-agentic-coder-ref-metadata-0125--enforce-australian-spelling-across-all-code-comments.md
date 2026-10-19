---
# holon-agentic-coder-ref-metadata-0125
title: "Enforce Australian English spelling across code comments and logging messages"
status: todo
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
updated_at: 2026-10-19T01:38:00Z
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

- [ ] Run automated wordlist scan for US spelling variants across Python and shell code.
- [ ] Exclude all `LICENSE` files, third-party vendor licenses, and upstream legal boilerplate from modification.
- [ ] Replace identified occurrences in code comments, docstrings, and log strings with standard Australian English
      equivalents (`initialise`, `behaviour`, `optimise`, `serialise`, `prioritise`).
- [ ] Add lint or regex hygiene check to prevent reintroduction of non-conforming spellings while maintaining license
      file exclusions.
