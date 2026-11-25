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
updated_at: 2026-11-25T01:03:00Z
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

> 2026-11-24: `Holon-Agentic-Coder/holon-coherence#56` (`coherence-final-self-doc`, head `faf37e06`, `7/7` CI checks
> green, Stage 4 APPROVED, Stage 5 calibrated EV `8.29` -> `8.84`) verified ready to merge (completing all Python and
> workflow/action YAML self-doc slices plus repo-wide enforcement in `holon-coherence`). Backfilled slot #3 with
> `config-env-self-doc` (`todo/intent-0153-config-env-self-doc.json`) via `antigravity-agent` / `gemini-4-neon`.

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
