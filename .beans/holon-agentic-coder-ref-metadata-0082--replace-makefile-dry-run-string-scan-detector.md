---
# holon-agentic-coder-ref-metadata-0082
title: "Replace the Makefile dry-run string scan with a reliable -n detector"
status: completed
type: task
priority: medium
tags:
  - makefile
  - prerequisites
  - dry-run
  - holon-agentic-coder
created_at: 2026-10-10T04:10:00Z
updated_at: 2026-10-12T09:20:00Z
---

## Summary

> [!CAUTION] **Correction, measured 2026-10-11: this is partly a regression, not purely pre-existing.** The framing
> below ("a pre-existing class rather than a regression the PR introduced") was **wrong** for the rewritten guard, and
> it was my own adjudication error: I carried a reviewer's claim across repositories without measuring it. Reproduced
> side by side on GNU Make 3.81 with the two guard expressions in `/tmp`:
>
> | invocation                                                       | old guard (`firstword`)       | new guard (`foreach` over words) |
> | ---------------------------------------------------------------- | ----------------------------- | -------------------------------- |
> | `make -I incdir_n probe`                                         | `RUN` (correct)               | **`SKIP` (false skip)**          |
> | `make DETECTED_OS=Linux probe`                                   | `SKIP` (the bug the PR fixes) | `RUN` (correct)                  |
> | `make -n probe`, `make -n -I incdir_n probe`, plain `make probe` | correct                       | correct                          |
>
> So the rewrite fixes the `VAR=value` false positive and **introduces** a `-I <path-containing-n>` false positive that
> the pre-PR code did not have. Finding reopened on PR #13 (holon-coherence) for that reason; see "Where the fix
> belongs" below.

Found while reviewing PR #69 (Bean 0079).

`holon-agentic-coder` guards its long recipes with an in-shell dry-run test that scans `MAKEFLAGS` for the letter `n` in
any token that is not a `VAR=value` assignment or a `--long` option. GNU Make stores option _arguments_ as separate bare
words in `MAKEFLAGS`, so a word made of letters that is not an option still matches the substring scan and the recipe
believes it is in dry-run mode.

Measured on GNU Make 3.81 by the reviewer passes:

- `make -I inc -f run.mk probe` → `MAKEFLAGS=[I inc]` → guard reports dry run → `check-prerequisites` prints its banner,
  runs **no** checks and exits **0**.
- `make -o foo.in ...` → same false positive.

A prerequisite check that silently reports success is the wrong failure mode, so the detection should stop being a
string scan: gate on a make-level sentinel computed from `MAKEFLAGS` words that can distinguish single-letter option
groups (`n`, `Bn`, `-qn`) from option arguments, or restructure the recipes so dry-run suppression lives in make
conditionals rather than in shell.

## Where the fix belongs

- **PR #13 (holon-coherence)**: the `-I <path-with-n>` false skip is introduced by this PR's rewrite and must be fixed
  there, not deferred - a `check-prerequisites` that prints its banner, checks nothing and exits 0 is exactly the
  silent-success class this review loop treats as blocking.
- **This bean** keeps the structural work: replacing the substring scan on both repositories once the immediate
  regression is contained.

## Scope

- `Makefile` targets `install-docker`, `check-docker`, `check-prerequisites` (all three carry the same guard).
- `apps/sandbox-executor/tests/test_makefile.py`: add dry-run-detector cases (`-I <dir>`, `-o <file.in>`, bundled `-Bn`,
  `--dry-run`, and a real GNU Make 4.x run on CI).
- Check whether `holon-coherence` carries the same guard pattern and needs the same fix.

## Progress & Resolution (2026-10-12)

- Fixed on `holon-agentic-coder` PR #69 (`89cede5`): the `MAKEFLAGS` word scan is replaced by `MF_OPTION_CLUSTER` /
  `DRY_RUN`, consulting only make's compacted leading option cluster.
- Mutation-proven by unit tests in `apps/sandbox-executor/tests/test_makefile.py`.
- Fixed on `holon-coherence` PR #13 (`d8e0564`).
- Both PR #69 and PR #13 are now merged into `origin/main`.
