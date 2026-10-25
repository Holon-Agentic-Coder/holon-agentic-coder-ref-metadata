---
# holon-agentic-coder-ref-metadata-0153
title:
  "Remove comments and docstrings from all code (Python, shell, JavaScript, build and CI files); make code
  self-documenting"
status: todo
type: task
priority: normal
tags:
  - code-smell
  - refactor
  - readability
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-25T07:42:56Z
updated_at: 2026-10-25T07:43:50Z
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

## Resolution
