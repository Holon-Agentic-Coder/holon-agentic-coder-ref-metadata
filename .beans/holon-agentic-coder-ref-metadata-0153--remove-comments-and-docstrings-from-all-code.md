---
# holon-agentic-coder-ref-metadata-0153
title:
  "Remove comments and docstrings from all code (Python, shell, JavaScript, build and CI files); make code
  self-documenting"
status: in-progress
type: task
priority: normal
tags:
  - code-smell
  - refactor
  - readability
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-25T07:42:56Z
updated_at: 2026-11-27T04:43:35Z
---

## Problem

The code depends on comments and docstrings to explain what it does. Code should be self-explaining in every language:
names should show the intent of every statement, and a block that can't be named where it sits should be extracted into
a function (or shell function, make variable or target, JS function) whose name says what it does. A comment that
explains code is a sign the code isn't clear enough. It also drifts out of date, because nothing checks it against the
code. This review loop kept finding stale prose: wrong line counts, "never printed" claims the code broke, outdated
sweep tables.

### Baseline (2026-10-25, `origin/main`: holon-agentic-coder `b3e2727`, holon-coherence `acbe924`)

**Python**

| Repository          | Files | Docstrings (lines) | Comment lines | Function docstrings | Module docstrings |
| ------------------- | ----- | ------------------ | ------------- | ------------------- | ----------------- |
| holon-agentic-coder | 68    | 921 (3,448)        | 1,509         | 761 of 1,794 fns    | 56                |
| holon-coherence     | 38    | 418 (1,026)        | 419           | 318 of 927 fns      | 35                |

The heaviest are `flow.py` (551 docstring lines and 120 comments) and `cli.py` (320 and 130). After them come
`entrypoint/executor.py` (203 and 102), `redaction.py` (213 and 39), `calibration.py` (181 and 26), and the tests
`test_executor.py`, `test_token_reduction.py`, `test_makefile.py` and coherence's `test_cli.py`.

**Other code (comment lines)**

- **holon-agentic-coder:**
  - `Makefile`: 31
  - `apps/sandbox-executor/Dockerfile`: 23
  - `entrypoint/role_dispatcher.sh`: 18
  - `build_all_images.sh`: 10
  - `.github/workflows/test-stress.yml`: 8
  - a few in `pyproject.toml`, `holon`, other workflows and `action.yml`
- **holon-coherence:**
  - `Makefile`: **157**. These are explanatory comments, not `make help` annotations; `help:` is a separate target.
  - `Dockerfile`: 3
  - `build_image.sh`: 2
  - `config/config.mk` and workflows: a few
- **JavaScript:** no `.js` files today. coherence's `mitm_addon.render_dashboard_html` (379 lines) embeds an HTML page
  with an inline `<script>` block. That JS is in scope too. Pulling it into a real asset file (with named functions)
  pairs with Bean 0152's decomposition of that function.

Neither repository's ruff config requires docstrings: `select` is `E W F I UP B C4 SIM RUF` in both.

## Scope

1. **All code, in every language:** Python (source and tests), shell scripts and the `holon` launcher, Makefiles and
   `*.mk`, Dockerfiles, GitHub workflow and action YAML, HCL, TOML config, and JavaScript (standalone or embedded). Any
   language added later is covered by the same rule.
   - **Out of scope, do not touch:** the markdown under `docs/`, READMEs and any other markdown.
2. **Replace prose with code:**
   - Rename variables, functions, parameters, constants, make variables and targets, shell functions and workflow
     step/job names until each statement's intent is clear without a comment.
   - Extract any block or expression that needed a comment into a named function (shell function, make variable or
     target, JS function, Python function or predicate), so the name carries what the comment said.
   - Replace magic values with named constants.
   - Give tests names that state the behaviour they check.
   - In YAML, prefer a descriptive `name:` on steps and jobs over a comment.
3. **Comments that may stay** are only those the toolchain needs, or that state a constraint the code can't express:
   - tool pragmas and directives, such as `# noqa`, `# type: ignore`, `# pragma: no cover`, `# fmt:`,
     `# shellcheck disable=`, `// eslint-disable-*` and `# syntax=` in Dockerfiles
   - shebangs and encoding lines
   - licence headers, if any
   - a reference to an external spec, upstream bug or vendor quirk where the reason really is outside the code (for
     example a GNU make version behaviour), cut to one line plus a link

   Each one is justified in the PR.

4. **Enforce it:** add a check run by `uv run task lint` (and CI) that fails on any docstring or non-allowlisted comment
   in every covered file type. Also enable ruff `ERA` (commented-out code). Use `shellcheck` for shell. This stops prose
   creeping back in.
5. **No behaviour change.**
   - The full suite, the URL fuzz tests, the `gh` write guard and `test_makefile.py` stay green.
   - User-facing output is not documentation of code and stays: CLI `--help` text (argparse `help=`), `make help`
     output, and log or error messages.
6. **Order and isolation:**
   - Do this with, or right after, Bean 0152's function decomposition, because extracting functions is how most comments
     get replaced.
   - Run one flow PR per module, package or file group (for example "Makefiles and shell", "CI workflows"), and never
     two at once on overlapping files (Bean 0151, and the sequential-overlapping-flows rule).
   - Start with files no open PR touches.

## Notes

- Run through the Holon flow, once per target repository and file group.
- Re-run the baseline count (Python AST pass plus a per-language comment count) after each PR and add the numbers here.
- Related: Bean 0152 (decompose oversized functions and split modules), Bean 0151 (planner touch sets with a hard block
  on overlapping concurrent flows).

> 2026-11-23: stale worktree deleted 2026-11-23; restart from current main. Backup:
> todo/stale-worktree-backups/flow-remove-comments-sandbox-shell-2026-11-23.bundle 2026-11-24: launched
> `holon-coherence` build/shell self-documenting slice (`coherence-build-self-doc`, intent
> `todo/intent-0153-coherence-build-self-doc.json`) via `antigravity-agent` / `gemini-4-argon`.

> 2026-11-24: `holon-coherence` build/shell slice (`coherence-build-self-doc`) delivered via
> [PR #45](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/45) and merged into `main` (`026b0a25`; 3/3
> consensus approved, 7/7 CI green, Stage 5 calibrated EV predicted `8.32` / actual `8.33` / delta `+0.01`),
> `holon-coherence` image & CLI rebuilt, and `flow-coherence-build-self-doc` worktree pruned.

> 2026-11-24: launched `holon-coherence` metrics/ab_testing self-documenting slice (`coherence-metrics-ab-self-doc`,
> intent `todo/intent-0153-coherence-metrics-ab-self-doc.json`) via `antigravity-agent` / `gemini-4-argon`.

> 2026-11-24: the `holon-coherence` metrics/ab_testing slice (`coherence-metrics-ab-self-doc`) was delivered via
> [PR #46](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/46) and merged into `main` (`5f7d6bbf`; 3/3
> consensus approved, 7/7 CI green, Stage 5 calibrated), `holon-coherence` image & CLI rebuilt, and
> `flow-coherence-metrics-ab-self-doc` pruned.

> 2026-11-24: launched `holon-coherence` container self-documenting slice (`coherence-container-self-doc`, intent
> `todo/intent-0153-coherence-container-self-doc.json`) via `antigravity-agent` / `gemini-4-argon`.

> 2026-11-24: launched `holon-coherence` parsers/providers self-documenting slice (`coherence-providers-self-doc`,
> intent `todo/intent-0153-coherence-providers-self-doc.json`) via `antigravity-agent` / `gemini-4-argon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#48` (`coherence-providers-self-doc`, parsers/ + providers/ slice)
> merged at `981a88a4` (3/3 approved, 7/7 CI green, Stage 5 calibrated), `apps/holon-coherence/main` was fast-forwarded,
> `holon-coherence` was rebuilt/reinstalled, and `flow-coherence-providers-self-doc` was pruned.

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#49` (`coherence-commands-self-doc`, `commands/` + `tests/commands/`
> slice) merged at `9c9310fc` (7/7 CI green, Stage 5 calibrated EV predicted `8.57` / actual `8.36` / delta `-0.21`),
> `apps/holon-coherence/main` fast-forwarded, `holon-coherence` rebuilt/reinstalled, and
> `flow-coherence-commands-self-doc` pruned.

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#50` (`coherence-proxy-self-doc`, `proxy/` + `tests/proxy/` slice)
> merged at `4469abc9` (7/7 CI green, Stage 5 calibrated), `apps/holon-coherence/main` fast-forwarded, `holon-coherence`
> rebuilt/reinstalled, and `flow-coherence-proxy-self-doc` pruned.

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#51` (`coherence-core-self-doc`, top-level `src/holon_coherence/*.py`
> slice) merged at `734e557` (7/7 CI green, Stage 5 calibrated EV predicted `8.65` / actual `8.96` / delta `+0.31`),
> `apps/holon-coherence/main` fast-forwarded, `holon-coherence` rebuilt/reinstalled, and `flow-coherence-core-self-doc`
> pruned.

> 2026-11-24: launched `holon-coherence` scripts and CI/hygiene/Makefile tests self-documenting slice
> (`coherence-scripts-self-doc`, intent `todo/intent-0153-coherence-scripts-self-doc.json`) via `antigravity-agent` /
> `gemini-4-neon`.

> 2026-11-24: launched `holon-coherence` CLI/coherence/host-local/hybrid-cache tests self-documenting slice
> (`coherence-cli-tests-self-doc`, intent `todo/intent-0153-coherence-cli-tests-self-doc.json`) via `antigravity-agent`
> / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#52` (`coherence-scripts-self-doc`, commit
> `c38beea5ac762922024e9ca1c59758d40576735f`) merged at `2026-11-24T10:56:55Z` (7/7 CI checks green, EV `8.56` ->
> `8.87`), covering the scripts self-doc slice. `apps/holon-coherence/main` fast-forwarded, `holon-coherence`
> rebuilt/reinstalled, and `flow-coherence-scripts-self-doc` worktree/branches pruned.

> 2026-11-24: launched `holon-coherence` mitmproxy addon and SSE tests self-documenting slice
> (`coherence-addon-tests-self-doc`, intent `todo/intent-0153-coherence-addon-tests-self-doc.json`) via
> `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#54` (`coherence-addon-tests-self-doc`, merge commit
> `ec0cd5a106ec3178c1d4f073c35fe8995399a712`, merged `2026-11-24T11:31:59Z`, 7/7 CI checks green, Stage 5 calibrated)
> landed cleanly, covering the final Python files in `holon-coherence` for Bean `0153`. `apps/holon-coherence/main`
> fast-forwarded, `holon-coherence` rebuilt/reinstalled, and `flow-coherence-addon-tests-self-doc` pruned.

- 2026-11-24 (clean-up): stays open. `holon-coherence` Python source and tests, build files and scripts are delivered by
  PRs #45 to #54 (Python files finished by #54 at 11:31Z). Remaining: every `holon-agentic-coder` slice (the slice
  `launcher-proxy-self-doc` has a worktree), and any `holon-coherence` Makefile or workflow comments not covered by #45.

> 2026-11-24: launched `holon-agentic-coder` launcher container/mount/dispatch self-documenting slice
> (`launcher-containers-self-doc`, intent `todo/intent-0153-launcher-containers-self-doc.json`) via `antigravity-agent`
> / `gemini-4-neon`.

> 2026-11-24: launched `holon-agentic-coder` CLI flow-helper and lifecycle commands self-documenting slice
> (`cli-commands-exec-self-doc`, intent `todo/intent-0153-cli-commands-exec-self-doc.json`) via `antigravity-agent` /
> `gemini-4-neon`.

> 2026-11-24: launched `holon-agentic-coder` CLI calibration/review/ledger commands self-documenting slice
> (`cli-commands-misc-self-doc`, intent `todo/intent-0153-cli-commands-misc-self-doc.json`) via `antigravity-agent` /
> `gemini-4-neon`.

> 2026-11-24: launched `holon-agentic-coder` E2E harness modules self-documenting slice (`e2e-self-doc`, intent
> `todo/intent-0153-e2e-self-doc.json`) via `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: launched `holon-agentic-coder` entrypoint execution-helper modules self-documenting slice
> (`entrypoint-exec-self-doc`, intent `todo/intent-0153-entrypoint-exec-self-doc.json`) via `antigravity-agent` /
> `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#284` (`e2e-self-doc`, head `0e964ec2`, Stage 4 3/3 approved,
> Stage 5 calibrated, 11/11 CI checks green) recovered after duplicate-run checkout hiccup and verified ready to merge.
> Backfilled slot #4 with `entrypoint-helpers-self-doc` (`todo/intent-0153-entrypoint-helpers-self-doc.json`) via
> `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#285` (`entrypoint-exec-self-doc`, head `0bd75b56`) completed
> Stage 4 consensus and Stage 5 calibration (`9/11` CI checks `SUCCESS`; re-triggered cancelled `build (macos-latest)`
> and `unit (macos-latest)`). Backfilled slot #3 with `ledger-self-doc` (`todo/intent-0153-ledger-self-doc.json`) via
> `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#285` (`entrypoint-exec-self-doc`, head `0bd75b56`, `11/11` CI
> checks green) and `Holon-Agentic-Coder/holon-agentic-coder#286` (`entrypoint-helpers-self-doc`, head `2ea6652b`,
> `11/11` CI checks green, Stage 4 3/3 approved, Stage 5 calibrated EV `40.61` -> `51.94`) both verified ready to merge.
> Backfilled slot #4 with `core-helpers-self-doc` (`todo/intent-0153-core-helpers-self-doc.json`) via
> `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: Backfilled slot #1 (vacated by `0376` PR #283) with `git-utils-self-doc`
> (`todo/intent-0153-git-utils-self-doc.json`) via `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#288` (`git-utils-self-doc`, head `baa3cc1b`, `11/11` CI checks
> green, Stage 4 APPROVED, Stage 5 calibrated EV `42.75` -> `57.21`) verified ready to merge. Backfilled slot #1 with
> `knowledge-self-doc` (`todo/intent-0153-knowledge-self-doc.json`) via `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#287` (`ledger-self-doc`, head `72d438b9`, calibrated, 9/11 CI
> checks `SUCCESS`; re-triggered cancelled `build (macos-latest)` while `unit (macos-latest)` is queued). Backfilled
> slot #3 with `infra-helpers-self-doc` (`todo/intent-0153-infra-helpers-self-doc.json`) via `antigravity-agent` /
> `gemini-4-neon`.

> 2026-11-24: `infra-helpers-self-doc` paused at Stage 3 after detecting a real `redaction.py` overlap with open
> `holon-agentic-coder#287` (waiting cleanly until `#287` merges). Filled active slot #3 in `holon-coherence` with
> `coherence-final-self-doc` (`todo/intent-0153-coherence-final-self-doc.json`, covering the final 2 Python test files,
> 3 YAML files, and repo-wide enforcement in `tests/test_repo_self_doc.py`) via `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#289` (`core-helpers-self-doc`, head `6f14049c`, `11/11` CI checks
> green, Stage 4 APPROVED at iter 3, Stage 5 calibrated EV `39.15` -> `49.09`) verified ready to merge. Backfilled slot
> #4 with `executor-pkg-self-doc` (`todo/intent-0153-executor-pkg-self-doc.json`) via `antigravity-agent` /
> `gemini-4-neon`.

> 2026-11-25: `Holon-Agentic-Coder/holon-coherence#56` (`coherence-final-self-doc`, head `faf37e06`, merge commit
> `18084f3a`, merged `2026-11-25T22:57:30Z`, 7/7 CI checks green, Stage 4 APPROVED, Stage 5 calibrated EV `8.29` ->
> `8.84`) merged into `main`, completing all Python and workflow/action YAML self-doc slices plus repo-wide enforcement
> in `holon-coherence`. `apps/holon-coherence/main` fast-forwarded to `18084f3a`, `holon-coherence` Docker image and CLI
> rebuilt/reinstalled via `install_coherence.py`, and `flow-coherence-final-self-doc` worktree plus
> `I-1795548977-coherence-final-self-doc/*` (local and remote) and `flow-coherence-final-self-doc` branches pruned. Bean
> `0153` stays `in-progress` while `holon-agentic-coder` slices remain.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#291` (`executor-pkg-self-doc`, head `5b386da1`, `11/11` CI checks
> green, Stage 4 APPROVED, Stage 5 calibrated EV `35.67` -> `48.36`) verified ready to merge. Backfilled slot #4 with
> `review-meta-self-doc` (`todo/intent-0153-review-meta-self-doc.json`) via `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#282` (`cli-commands-misc-self-doc`, merge commit `b8093ff6`,
> merged `2026-11-24T20:46:19Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded, `holon`
> rebuilt/reinstalled, and `flow-cli-commands-misc-self-doc` worktree/branches pruned.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#290` (`knowledge-self-doc`, head `57152552`, `P-1795547238`
> calibrated) completed all 5 stages before transient host DNS interruption (`21:21Z`); needs ledger merge after `#283`
> merges. Backfilled slot #2 with `git-flow-self-doc` (`todo/intent-0153-git-flow-self-doc.json`) via
> `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#293` (`review-meta-self-doc`, head `995bd4c2`, `11/11` CI checks
> green, calibrated EV `35.20` -> `44.47`) verified ready to merge (`#283` also settled ledgers `91b23ee9`, `MERGEABLE`
> / `CLEAN`, `11/11` CI `SUCCESS`). Backfilled slot #4 with `local-llm-self-doc`
> (`todo/intent-0153-local-llm-self-doc.json`) via `antigravity-agent` / `gemini-4-neon`.

> 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#276` (`launcher-proxy-self-doc`, merge commit `e1d1ae37`, merged
> `2026-11-24T23:43:09Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded, Docker images and
> `holon`/`holon-coherence` CLIs rebuilt and reinstalled via `install_holon.py`, and `flow-launcher-proxy-self-doc`
> worktree plus `I-1795524475-launcher-proxy-self-doc/*`, `I-1795524794-launcher-proxy-self-doc/*`, and
> `flow-launcher-proxy-self-doc` branches pruned.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#280` (`launcher-containers-self-doc`, merge commit `131c3b42`,
> merged `2026-11-25T01:01:13Z`; 3/3 consensus approved, 11/11 CI green, Stage 5 calibrated) merged into `main`.
> `apps/holon-agentic-coder/main` fast-forwarded to `131c3b42`, `holon` images and CLI rebuilt/reinstalled via
> `install_holon.py --holon-only`, and `flow-launcher-containers-self-doc` worktree plus
> `I-1795530292-launcher-containers-self-doc/*` (local and remote) and `flow-launcher-containers-self-doc` branches
> pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#301` (`preflight-self-doc`, head `74a5ce76`, 3/3 consensus
> approved at iter 1, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `46.47` -> `55.27`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#302` (`review-report-self-doc`, head `7ccad6b4`, 3/3 consensus
> approved at iter 1, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `36.85` -> `44.76`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge. Backfilled active flow slots with `agent-defaults-self-doc` and `github-ci-self-doc`.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#300` (`decomposition-rule-self-doc`, head `4c86f067`, 3/3
> consensus approved at iter 2, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `49.69` -> `58.62`, `MERGEABLE`/`CLEAN`)
> completed all 5 stages and is ready to merge. Backfilled active flow slot with `git-refs-self-doc`.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#303` (`agent-defaults-self-doc`, head `8683fb18`, 3/3 consensus
> approved at iter 1, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `36.65` -> `44.47`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge. Backfilled active flow slot with `github-pr-merge-self-doc`.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#304` (`github-ci-self-doc`, head `0f32de55`, 3/3 consensus
> approved at iter 1, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `33.95` -> `42.06`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge. Backfilled active flow slot with `github-misc-self-doc`.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#305` (`git-refs-self-doc`, head `11334f7a`, 3/3 consensus
> approved at iter 2, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `41.01` -> `48.79`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge. Holding further `Bean 0153` backfills until open PRs merge.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#307` (`github-misc-self-doc`, head `aa8cd726`, 3/3 consensus
> approved at iter 1, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `46.10` -> `55.45`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge. Holding further `Bean 0153` backfills until open PRs merge.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#281` (`cli-commands-exec-self-doc`, merge commit `c93bb9eb`,
> merged `2026-11-25T02:08:49Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `c93bb9eb`,
> `holon` images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-cli-commands-exec-self-doc`
> worktree plus `I-1795532856-cli-commands-exec-self-doc/*` (local and remote) and `flow-cli-commands-exec-self-doc`
> branches pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#306` (`github-pr-merge-self-doc`, head `928446ed`, 3/3 consensus
> approved at iter 2, 11/11 CI `SUCCESS`, Stage 5 calibrated EV `39.38` -> `46.51`, `MERGEABLE`/`CLEAN`) completed all 5
> stages and is ready to merge. Holding further `Bean 0153` backfills until open PRs merge.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#284` (`e2e-self-doc`, merge commit `1a5c69d6`, merged
> `2026-11-25T02:47:53Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `1a5c69d6`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-e2e-self-doc` worktree plus
> `I-1795536007-e2e-self-doc/*` (local and remote) and `flow-e2e-self-doc` branches pruned. Bean `0153` stays
> `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#285` (`entrypoint-exec-self-doc`, merge commit `2305219e`, merged
> `2026-11-25T02:58:51Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `2305219e`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-entrypoint-exec-self-doc` worktree
> plus `I-1795539256-entrypoint-exec-self-doc/*` (local and remote) and `flow-entrypoint-exec-self-doc` branches pruned.
> Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#286` (`entrypoint-helpers-self-doc`, merge commit `0ba99e0c`,
> merged `2026-11-25T03:07:49Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `0ba99e0c`,
> `holon` images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-entrypoint-helpers-self-doc`
> worktree plus `I-1795540468-entrypoint-helpers-self-doc/*` (local and remote) and `flow-entrypoint-helpers-self-doc`
> branches pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#287` (`ledger-self-doc`, merge commit `522293a6`, merged
> `2026-11-25T03:21:48Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `522293a6`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-ledger-self-doc` worktree plus
> `I-1795543016-ledger-self-doc/*` (local and remote) and `flow-ledger-self-doc` branches pruned. Bean `0153` stays
> `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#288` (`git-utils-self-doc`, merge commit `558646ae`, merged
> `2026-11-25T03:35:55Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `558646ae`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-git-utils-self-doc` worktree plus
> `I-1795544951-git-utils-self-doc/*` (local and remote) and `flow-git-utils-self-doc` branches pruned. Bean `0153`
> stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#289` (`core-helpers-self-doc`, merge commit `c0a183f4`, merged
> `2026-11-25T03:42:30Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `c0a183f4`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-core-helpers-self-doc` worktree plus
> `I-1795544814-core-helpers-self-doc/*` (local and remote) and `flow-core-helpers-self-doc` branches pruned. Bean
> `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#290` (`knowledge-self-doc`, merge commit `ae2c5b41`, merged
> `2026-11-25T03:58:54Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `ae2c5b41`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-knowledge-self-doc` worktree plus
> `I-1795547220-knowledge-self-doc/*` (local and remote) and `flow-knowledge-self-doc` branches pruned. Bean `0153`
> stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#291` (`executor-pkg-self-doc`, merge commit `4da9b33b`, merged
> `2026-11-25T04:11:48Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `4da9b33b`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-executor-pkg-self-doc` worktree plus
> `I-1795549499-executor-pkg-self-doc/*` (local and remote) and `flow-executor-pkg-self-doc` branches pruned. Bean
> `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#292` (`config-env-self-doc`, merge commit `301f8fdb`, merged
> `2026-11-25T04:49:53Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `301f8fdb`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and `flow-config-env-self-doc` worktree plus
> `I-1795551241-config-env-self-doc/*` (local and remote) and `flow-config-env-self-doc` branches pruned. Bean `0153`
> stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#293` (`review-meta-self-doc`, merge commit `daf3fa74`, merged
> `2026-11-25T04:52:30Z`) and `Holon-Agentic-Coder/holon-agentic-coder#294` (`git-flow-self-doc`, merge commit
> `d87d9823`, merged `2026-11-25T04:55:29Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to
> `d87d9823`, `holon` images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and
> `flow-review-meta-self-doc` / `flow-git-flow-self-doc` worktrees plus `I-1795552034-review-meta-self-doc/*`,
> `I-1795560404-git-flow-self-doc/*` (local and remote), and `flow-*` branches pruned. Bean `0153` stays `in-progress`
> for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#295` (`local-llm-self-doc`, merge commit `099025f8`, merged
> `2026-11-25T04:59:58Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `origin/main`
> (`4c6232cb`, which already includes `099025f8` and `#296`), `holon` images and CLI rebuilt/reinstalled via
> `install_holon.py --holon-only`, and `flow-local-llm-self-doc` worktree plus `I-1795561357-local-llm-self-doc/*`
> (local and remote) and `flow-local-llm-self-doc` branches pruned. Bean `0153` stays `in-progress` for the remaining
> slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#297` (`claude-auth-self-doc`, merge commit `0bd580ea`, merged
> `2026-11-25T05:09:36Z`) and `Holon-Agentic-Coder/holon-agentic-coder#298` (`touch-set-self-doc`, merge commit
> `5e08904f`, merged `2026-11-25T05:12:10Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to
> `5e08904f`, `holon` images and CLI rebuilt/reinstalled via `install_holon.py --holon-only`, and
> `flow-claude-auth-self-doc` / `flow-touch-set-self-doc` worktrees plus `I-1795563579-claude-auth-self-doc/*`,
> `I-1795565481-touch-set-self-doc/*` (local and remote), and `flow-*` branches pruned. Bean `0153` stays `in-progress`
> for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#300` (`decomposition-rule-self-doc`, merge commit `efafa316`)
> merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `efafa316`, `holon` images and CLI
> rebuilt/reinstalled via `install_holon.py --holon-only` (`holon --help` exit 0), and
> `flow-decomposition-rule-self-doc` worktree plus `I-1795567884-decomposition-rule-self-doc/*` (local and remote) and
> `flow-decomposition-rule-self-doc` branches pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#301` (`preflight-self-doc`, merge commit `ebcffd12`) merged into
> `main`. `apps/holon-agentic-coder/main` fast-forwarded to `ebcffd12`, `holon` images and CLI rebuilt/reinstalled via
> `install_holon.py --holon-only` (`holon --help` exit 0), and `flow-preflight-self-doc` worktree plus
> `I-1795567888-preflight-self-doc/*` (local and remote) and `flow-preflight-self-doc` branches pruned. Bean `0153`
> stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#302` (`review-report-self-doc`, merge commit `67bfb621`),
> `Holon-Agentic-Coder/holon-agentic-coder#303` (`agent-defaults-self-doc`, merge commit `d281e437`), and
> `Holon-Agentic-Coder/holon-agentic-coder#304` (`github-ci-self-doc`, merge commit `bdb2d5f1`) merged into `main`.
> `apps/holon-agentic-coder/main` fast-forwarded to `bdb2d5f1`, `holon` images and CLI rebuilt/reinstalled via
> `install_holon.py --holon-only` (`holon --help` exit 0), and `flow-review-report-self-doc`,
> `flow-agent-defaults-self-doc`, and `flow-github-ci-self-doc` worktrees plus `I-1795567884-review-report-self-doc/*`,
> `I-1795569457-agent-defaults-self-doc/*`, `I-1795569528-github-ci-self-doc/*` (local and remote) and `flow-*` branches
> pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#305` (`git-refs-self-doc`, merge commit `6df29342`, merged
> `2026-11-25T06:12:01Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `6df29342`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only` (`holon --help` exit 0), and
> `flow-git-refs-self-doc` worktree plus `I-1795569615-git-refs-self-doc/*` (local and remote) and
> `flow-git-refs-self-doc` branches pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#306` (`github-pr-merge-self-doc`, merge commit `867f029f`, merged
> `2026-11-25T06:51:27Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `867f029f`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only` (`holon --help` exit 0), and
> `flow-github-pr-merge-self-doc` worktree plus `I-1795570951-github-pr-merge-self-doc/*` (local and remote) and
> `flow-github-pr-merge-self-doc` branches pruned. Bean `0153` stays `in-progress` for the remaining slices.

> 2026-11-25: `Holon-Agentic-Coder/holon-agentic-coder#307` (`github-misc-self-doc`, merge commit `e1f63aae`, merged
> `2026-11-25T06:54:51Z`) merged into `main`. `apps/holon-agentic-coder/main` fast-forwarded to `e1f63aae`, `holon`
> images and CLI rebuilt/reinstalled via `install_holon.py --holon-only` (`holon --help` exit 0), and
> `flow-github-misc-self-doc` worktree plus `I-1795570995-github-misc-self-doc/*` (local and remote) and
> `flow-github-misc-self-doc` branches pruned. Bean `0153` stays `in-progress` for the remaining slices.

Note (2026-11-25): stale plan `infra-helpers-self-doc` deleted after PR #309 merged; restart from current main via the
kept `todo/intent-0153-infra-helpers-self-doc.json`.

> 2026-11-27: launched `holon-agentic-coder` self-explaining code gate slice (`self-explaining-code-gate`, intent
> `todo/intent-0153-self-explaining-code-gate.json`; diff-scoped hygiene check, lint/pre-commit/CI wiring and prompt
> invariant) via `claude-agent` / `claude-opus-5-5`, flow branch `flow-self-explaining-code-gate`.

> 2026-11-27: PR [#356](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/356)
> (`secret-bundle-private-files`, merged `d3c68686`) added two docstrings to
> `apps/sandbox-executor/src/sandbox_executor/agent_runner.py` (the owner-only directory and file writers) against this
> bean's self-explaining invariant. Remove them in the `holon-agentic-coder` clean-up slice.

Note (2026-11-26): [PR #351](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/351) (`2f29d8c`, beans
0390/0472) added 76 docstring lines (non-test `.py`, triple-quote delimiters included) and 11 comment lines against the
self-explaining-code invariant. Measured from `gh pr diff 351`; clean-up needed.

Note (2026-11-27): [PR #353](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/353) (`e9db3048`,
bean 0514) added 11 lines carrying triple quotes (docstring openers and closers, including one-line docstrings) and 4
comment lines in code files against the self-explaining-code invariant: 1 explanatory comment in
`scripts/ci_main_push_gate.py` and 3 `# ---` banner comments in
`apps/sandbox-executor/tests/test_ci_main_push_superseded.py`. Measured from `gh pr diff 353`. Clean-up needed.

Note (2026-11-26): PR #344 (bean 0506, `f37c1855`) added 14 docstring lines in its prune script
(`scripts/prune_kb_single_flow_failures.py`) during its clean-up; the self-explaining sweep should remove them with the
rest.

## Note (2026-11-27)

PR #358 (bean 0491, merged `14376ba5`) added 3 docstrings and one `#:` comment in
`apps/sandbox-executor/tests/conftest.py` and `apps/sandbox-executor/tests/test_fixture_discovery_subset.py` (measured
from `git show 14376ba5`: 75 added lines, 5 triple-quote delimiters, 1 `#:` line). The self-explaining-code gate did not
catch them; logged as bean 0574.

> 2026-11-27: flow `self-explaining-code-gate` (intent `todo/intent-0153-self-explaining-code-gate.json`) delivered the
> diff-scoped self-explaining gate via [PR #357](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/357),
> merged into `main` at `5a2868af` (Stage 4 consensus 3/3 APPROVED at iteration 4; Stage 5 calibrated, EV predicted
> `41.45` / actual `59.50`; 11/11 CI green). The gate runs in the `lint` task, the staged-files mode of
> `scripts/pre_commit_check.py` and `test-hygiene.yml`; the four agent prompt templates state the invariant. Fail-closed
> behaviour without a merge base is bean 0558.
>
> Remaining clean-up slices: the `holon-agentic-coder` docstrings and comments that landed after the gate's baseline
> (PRs #344, #351, #353, #356, #358 per the notes above) and the checkpoint path that dropped the invariant (bean 0574).
> Bean stays `in-progress`.

2026-11-27T00:32:54Z: PR #366 (module-budget-label-actor, merged f006e79b) added 0 docstrings. Two non-`# why:` comment
tokens: the shebang on line 1 of `scripts/check_module_budget_label_actor.py` and a `# type: ignore[arg-type]` pragma on
line 102 of `apps/sandbox-executor/tests/test_check_module_budget_label_actor.py`. Neither explains code; both are left
for the maintainer to decide. Bean stays in-progress.

## Note (2026-11-27T00:58:37Z): measured on origin/main e189a89f

Scanned every tracked file of `main` with the self-explaining checker rules (docstrings and comments other than `# why:`
and machine directives): 6740 findings, 3907 docstrings (function 2873, module 605, class 429) and 2833 comments. 6250
of them sit in `apps/sandbox-executor`; the rest are in CI workflows and actions, scripts and Makefile or pyproject.
Scanned from a `git archive` export, not the main worktree. Bean stays in-progress.

> 2026-11-27: `sandbox_executor` `flow/review` slice (`self-doc-src-28`, intent `todo/intent-0153-self-doc-src-28.json`)
> delivered via [PR #402](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/402) and merged into `main`
> (`3a9fc789`). Behaviour kept: string literals and function/class signatures match before and after in all 10 files; CI
> green on the final head. Counts (AST docstrings, tokenize comments; allowlist as the slice test): slice 73 docstrings
> (186 lines) and 16 disallowed comments before, 0 and 0 after. Package `apps/sandbox-executor/src/sandbox_executor`
> (370 files): 1564 docstrings (4603 lines) and 565 comments before; 1491 and 549 after #402; 1326 and 510 on `main`
> `0648afd0` after later slices. Bean stays `in-progress`: other packages, the test tree, and non-Python files still
> carry docstrings or comments.

> 2026-11-27: `holon-agentic-coder` slice `self-doc-src-27` (the `flow/review` package: 10 modules plus
> `tests/test_self_doc_src_27.py`) delivered via
> [PR #401](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/401) and merged into `main` (`7f82e0f1`).
> Self-explaining checker on `apps/sandbox-executor/src/sandbox_executor/flow/review` (docstrings and non-`# why:`
> comments): 318 before (`3a9fc789`: 33 module, 19 class, 176 function docstrings, 90 comments) and 239 after
> (`7f82e0f1`: 23, 13, 123, 80), so -79. The 10 listed modules went from 79 to 0. Code tokens are unchanged, but the
> `# Lazy:` import reasons were dropped rather than kept as `# why:` comments. The PR body carried no before/after
> counts. Bean stays `in-progress`.

## Note (2026-11-27T04:37Z): self-doc-src-i merged

Slice `self-doc-src-i` (10 sandbox-executor flow modules plus `tests/test_self_doc_src_i.py`) merged as
[PR #392](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/392) into `main` at `05b726e`.

- Counts on the scope files, merge parent vs merge commit: docstrings 79 to 0; plain comments 25 to 0 (all 25
  non-allowed); `# why:` comments 0 to 37. At most 25 of the 37 can be rewritten removed comments; the rest carry
  reasons from removed docstrings. The scan does not split them further.
- Acceptance scan (static AST and tokenize equivalent of the slice test) passes on the merged content. The in-tree test
  was not run under pytest.
- Approval at merge: 3/3 ensemble APPROVED (0 critical, 0 important, 0 nit) at `d9ced1d6`; calibration report present
  (`4f8618ae`). CI was 14/14 at `d9ced1d6`. Merge commit `05b726e` came from head `f6be399` (merge of main), which had
  13 checks still queued at merge and was not covered by the approval.

## Acceptance

- [ ] A check run by `uv run task lint`, pre-commit and CI fails on any docstring or non-allowlisted comment (delivered
      by PR #357; diff-scoped, fail-closed without a merge base is bean 0558, checkpoint-path gap is bean 0574).
- [ ] The four agent prompt templates state the self-explaining invariant (delivered by PR #357).
- [ ] `holon-coherence` Python source and tests, build files, scripts and workflow YAML have no docstrings and no
      comments except `# why:` and machine directives (delivered by PR #45, #46, #48, #49, #50, #51, #52, #54, #56).
- [ ] Every module under `apps/sandbox-executor/src/sandbox_executor/` has no docstrings and no comments except `# why:`
      and machine directives; behaviour unchanged (full suite green); module budgets unchanged. Earlier slices delivered
      by PR #276, #280, #282, #284 to #295, #297 to #307 and the slices merged after them.
- [ ] Every test module under `apps/sandbox-executor/tests/` has no docstrings and no comments except `# why:` and
      machine directives; behaviour unchanged (full suite green); module budgets unchanged.
- [ ] The docstrings and comments added by PRs #344, #351, #353, #356, #358 and #366 are removed (files named in the
      notes, including `agent_runner.py`, `scripts/prune_kb_single_flow_failures.py`, `scripts/ci_main_push_gate.py`,
      `tests/conftest.py`, `tests/test_fixture_discovery_subset.py`, `tests/test_ci_main_push_superseded.py`).
- [ ] Shell scripts, the `holon` launcher, Makefiles, Dockerfiles, CI workflow and action YAML, pyproject and scripts of
      `holon-agentic-coder` have no comments except `# why:` and machine directives; behaviour unchanged.
- [ ] Every remaining comment that stays is a tool directive, shebang, licence header or one-line external reference,
      justified in the PR.
- [ ] CLI `--help` text, `make help` output, and log or error messages are unchanged.
- [ ] The self-explaining checker reports zero findings on `main` (baseline 2026-11-27 on `e189a89f`: 6740 findings,
      3907 docstrings, 2833 comments).
- [ ] Each clean-up PR reports the before and after finding count for its slice.

> 2026-11-27: `apps/sandbox-executor` flow-stages slice (`self-doc-src-24`: 10 modules under `flow/stages/` plus
> `tests/test_self_doc_src_24.py`) delivered via
> [PR #397](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/397) and merged into `main` (`0648afd0`).
> Counts on those 10 files (ast/tokenize, `# why:` and directives allowed): before 96 docstrings (214 lines) and 29
> other comments; after 0 and 0. Bean stays in-progress: the rest of the sandbox-executor `src` and tests,
> shell/Make/CI/Dockerfile files, and the lint gate remain. PR #397 body reports no before/after counts (criterion 3 not
> met by the PR itself).

> 2026-11-27: `apps/sandbox-executor` flow slice (`self-doc-src-23`: target-sync, checkpoint, adoption and evidence
> modules under `flow/`, plus `tests/test_self_doc_src_23.py`) delivered via
> [PR #394](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/394) and merged into `main` (`41f6469`).
> Counts on the 10 existing scope files (ast/tokenize, before to after): docstring lines 137 to 0; non-allowed comments
> 9 to 0; `# why:` comments 0 to 29. Per file (docstring lines, comments): `stages/__init__.py` 1 to 0;
> `target_sync_branch.py` 5 to 0; `target_sync_hooks.py` 10 to 0; `target_sync_merge.py` 36 to 0 and 5 to 0;
> `target_sync_record.py` 11 to 0; `target_sync_result.py` 16 to 0; `target_sync_resume.py` 13 to 0 and 1 to 0;
> `test_evidence.py` 13 to 0 and 1 to 0; `unrecorded_branch_adoption.py` 23 to 0; `worktree_checkpoints.py` 9 to 0 and 2
> to 0. Reason comments deleted rather than rewritten as `# why:` (9): "Every merge the sync starts carries this
> message"; "the merge commit (with its row) has landed"; "the merge commit (with its row) already landed"; "the row may
> create its fragment"; "an empty pathspec would make `git commit --` commit the whole index"; "a failed push keeps the
> recorded merge commit"; "The optional executions.jsonl summary-row keys that describe a Stage 3 test measurement";
> "the current stage is execute or review"; "stale or foreign: never blocks". Still open: the other sandbox-executor src
> and test slices, shell/Makefile/Dockerfile/CI files, the holon-coherence sweep and the zero-findings checker on
> `main`; the bean stays `in-progress`.

> 2026-11-27: `apps/sandbox-executor` flow slice `self-doc-src-j` (10 modules under `flow/` plus
> `tests/test_self_doc_src_j.py`) delivered via
> [PR #399](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/399) and merged into `main` (`10088fa1`).
> Counts on those 10 source files (ast/tokenize, `# why:` and directives allowed): before 72 docstrings (190 lines) and
> 7 other comments; after 0 and 0. The slice test file (32 tests) passes on the identical slice files. Bean stays
> in-progress: the rest of the sandbox-executor `src` and tests, shell/Make/CI/Dockerfile files, and the lint gate
> remain.

> 2026-11-27: `apps/sandbox-executor` flow stages and review slice (`self-doc-src-25`: 10 modules under `flow/stages/`
> and `flow/review/` plus `tests/test_self_doc_src_25.py`) delivered via
> [PR #398](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/398) and merged into `main` (`d3982e76`).
> Counts on those 10 files (ast/tokenize, `# why:` and directives allowed): before 60 docstrings and 2 other comments;
> after 0 and 0, with 11 `# why:` comments kept. The 2 pre-existing comments in `stage_support.py` were rewritten as
> `# why:`; none were deleted. Bean stays in-progress: the rest of the sandbox-executor `src` and tests,
> shell/Make/CI/Dockerfile files, and the lint gate remain.

> 2026-11-27: `apps/sandbox-executor` flow-review slice (`self-doc-src-26`: 10 modules under `flow/review/` plus
> `tests/test_self_doc_src_26.py`) delivered via
> [PR #400](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/400) and merged into `main` (`1683f9f1`).
> Counts on those 10 files (ast/tokenize, `# why:` and directives allowed): before 84 docstrings and 17 other comments;
> after 0 and 0 (21 `# why:` comments kept). Whole-repo checker (`scripts/self_explaining_comments.py` over tracked
> files): `10088fa1` 6300 findings, `1683f9f1` 6199. Bean stays in-progress: the remaining sandbox-executor `src` and
> tests, shell/Make/CI/Dockerfile files, and the lint gate remain.

## Assumptions

- The checker rule set is the one in the gate delivered by PR #357 (`# why:` and machine directives allowed). Validated
  by running the checker on `main` and on each slice.
- Shebangs and `# type: ignore` pragmas count as machine directives. Validated by the checker's allowlist; the
  maintainer decides the PR #366 cases.
- ERA (commented-out code) and shellcheck enforcement from the original scope are covered by the gate. Validated by
  reading the gate's configuration before closing the bean.

> 2026-11-27: slice `self-doc-src-21` (the ten `sandbox_executor/flow/` modules, test `tests/test_self_doc_src_21.py`)
> delivered via [PR #396](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/396) and merged into `main`
> (`f90c47d3`). Acceptance on the merged tree, measured with `scripts/self_explaining_comments.py` on `git archive`
> copies (never the main worktree): scope modules 131 findings before (10 module docstrings, 5 class docstrings, 81
> function docstrings, 35 comments) and 0 after; `test_self_doc_src_21.py` 33 passed. Whole holon-agentic-coder `.py`
> tree (same finder): 5888 findings before (525 module, 368 class, 2436 function docstrings, 2559 comments) and 5757
> after (515, 363, 2355, 2524). Reason comments deleted rather than rewritten as `# why:`: "The branch each stage reads
> from the flow context and fails without (Stage 1 needs none)." and "an unlimited stage never overruns" on the
> `budget_seconds is None` line; the `#:` attribute docs that only described names were deleted with their names kept.
> Bean stays `in-progress` for the remaining holon-agentic-coder slices.
>
> 2026-11-27: slice `self-doc-tests-a` (15 test modules under `apps/sandbox-executor/tests/`) delivered via
> [PR #390](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/390) and merged into `main` (`de1cca2c`).
> Acceptance on the merged tree, measured with the `scripts/self_explaining_comments.py` finder on `git archive` copies
> (never the main worktree): scope modules 777 findings before (282 docstrings, 495 comments) and 0 after. 238 reason
> comments kept as `# why:` (rewritten); the rest deleted. Review loop: iteration 1 CHANGES_REQUESTED, iteration 2
> APPROVED by 3 of 3 reviewers; calibration report recorded before merge. GitHub shows no formal approving review (one
> COMMENTED review), so the approval is the review-loop ledger. Bean stays `in-progress` for the remaining
> holon-agentic-coder slices.

> 2026-11-27: slice `self-doc-src-g` (the ten `sandbox_executor/flow/` modules `admission*.py`, `base_files.py`,
> `calibrate_fetch_retry.py`, `calibrate_promotion.py`, `calibrate_rebuild.py`; test `tests/test_self_doc_src_g.py`)
> delivered via [PR #393](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/393) and merged into `main`
> (`055fb4a3`). Acceptance on the merged tree, measured with `scripts/self_explaining_comments.py` on
> `git archive`-style copies (never the main worktree): scope modules 69 findings before (10 module docstrings, 6 class
> docstrings, 37 function docstrings, 16 comments) and 0 after; 22 `# why:` comments now stand where none existed
> before. `test_self_doc_src_g.py`: 21 passed. Reason comments: the diff rewrites the reasons as `# why:` lines and
> deletes the descriptive ones (names kept). Bean stays `in-progress`: the remaining sandbox-executor slices,
> shell/Make/CI/Dockerfile files and the lint gate remain.

> 2026-11-27: slice `self-doc-src-f` (ten `sandbox_executor` modules in knowledge, entrypoint and flow; test
> `tests/test_self_doc_src_f.py`) delivered via
> [PR #389](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/389) and merged into `main` (`c0b41e27`).
> Acceptance on the merged tree, counted with an ast and tokenize pass on `git archive` copies (never the main
> worktree): scope modules 80 docstrings and 76 comments before (`de1cca2c`) and 0 and 0 after; 64 `# why:` comments
> kept (the reasons rewritten, the rest of the removed items deleted); 5 directive comments unchanged. Approval 3/3 was
> on `9991b03`; the scope files are identical at `9991b03`, the final head `b82a1cc` and the merge. Calibration was in
> the PR diff, not a separate pass after merge. Bean stays `in-progress` for the remaining holon-agentic-coder slices.

> 2026-11-27: slice `self-doc-root-modules-a` (15 `sandbox_executor` modules under `src/sandbox_executor/` plus the new
> `tests/test_self_doc_root_modules_a.py`) delivered via
> [PR #383](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/383) and merged into `main` (`acdd3fc`).
> Acceptance on the merged tree, counted with an ast and tokenize pass on `git archive`-style copies (never the main
> worktree): scope files before (`acdd3fc^`) 116 docstrings and 41 comments; after 0 and 0, with 40 `# why:` comments
> kept and 3 directive comments unchanged. Reason comments deleted rather than rewritten as `# why:` (verbatim,
> pre-merge line numbers): `agent_runner.py:55` "# Directory cleanup and root protection helpers"; `agent_runner.py:360`
> "# Ephemeral Secret Bundle Injection (HOLON_SECRET_BUNDLE_PATH or default /run/secrets/holon_auth.json)";
> `agent_runner.py:372` "# Unpack session files into /home/holon/ if specified"; `agent_runner.py:699` "# Runner
> registry: maps agent_id -> StandardAgentRunner instance." (the last three describe code and are the rename-or-extract
> case; the first is a section label). Flow worktree, its local and remote I-branches removed after a bundle backup at
> `todo/stale-worktree-backups/self-doc-root-modules-a-2026-11-27.bundle`. Bean stays `in-progress` for the remaining
> holon-agentic-coder slices.
