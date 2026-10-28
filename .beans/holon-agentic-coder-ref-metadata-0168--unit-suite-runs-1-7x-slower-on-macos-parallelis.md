---
# holon-agentic-coder-ref-metadata-0168
title: "Unit suite runs about 1.7x slower on macOS than Linux; parallelise it and cut per-test subprocess cost"
status: in-progress
type: task
priority: high
tags:
  - ci
  - performance
  - tests
  - holon-agentic-coder
created_at: 2026-10-27T10:26:52Z
updated_at: 2026-10-27T12:17:15Z
---

## Problem

On holon-agentic-coder PR #97 head `3e21065` (2026-10-27) both unit jobs ran the same 2443 tests:

| Job                    | "Run unit tests" step | pytest time | All other steps |
| ---------------------- | --------------------- | ----------- | --------------- |
| `unit (macos-latest)`  | 377 s                 | 374 s       | about 13 s      |
| `unit (ubuntu-latest)` | 227 s                 | 225 s       | about 5 s       |

The gap is entirely pytest time, about 1.66x. Setup is negligible. The suite runs **serially**:
`.github/workflows/test-unit.yml` passes no `-n`, and pytest-xdist is not a dependency. macOS run times also vary by
about ±20% between runs of the same code (523-776 s pytest time across PR #97 heads before the canary fix).

Likely causes, ranked. None has yet been measured per test.

1. **Subprocess spawning costs more on macOS.** The suite spawns many processes: `git` for the bare-repo and worktree
   fixtures throughout `test_flow.py` and `test_executor.py`, `uv`/`python` child runs, and CLI invocations. Each
   fork/exec on macOS pays dyld and code-signing overhead.
2. **Small-file filesystem work is slower** on hosted macOS VMs (APFS) than on Linux ext4. The tests create, write and
   delete many temporary repositories and files.
3. **Hosted macOS runners are smaller and shared VMs**, which shows up as higher variance.

## Scope

1. **Measure first, on real CI data only (AGENTS.md item 10).** Run the unit job with `--durations=50`, or a JUnit XML
   report, on both OSes for the same commit. Compare the slowest tests and the total time per test file. Count the
   subprocess calls per test, for example with a fixture that wraps `subprocess.Popen` in an audit-only mode. Confirm or
   reject the ranked causes.
2. **Parallelise.** Add pytest-xdist (`-n auto`, or a tuned worker count per OS) to the unit job and to
   `uv run task test`. First make the suite safe for parallel workers:
   - per-worker temporary directories and ledgers;
   - no shared fixed `/tmp` names;
   - no tests that depend on global environment or current-working-directory state;
   - the hermetic sandbox guard, and the stress-marked canary, working under xdist.

   Fix or quarantine order-dependent tests rather than serialising the whole suite.

3. **Cut per-test subprocess cost.** Build a template bare repository and worktree once per session and copy it per test
   instead of running `git init`/`commit`/`push` each time. Replace `git` calls with in-process equivalents where a test
   does not need real git behaviour. Avoid spawning `uv run` for child pytest runs except in the stress canary.
4. **Report.** Give before and after times per OS, both the "Run unit tests" step and the pytest time. Also show the
   ratio between the two OSes. Set the Bean 0163 baselines and ceilings from the new numbers.

## Notes

- Run through the Holon flow on holon-agentic-coder. It touches tests, fixtures, pyproject and workflows. Check for
  overlap with open flows (Bean 0151 touch-set rule).
- Related: Bean 0163 (CI timing regression gate), Bean 0166 (pipeline duration dashboard: collect per-test timings
  there), Bean 0167 (turn-supervisor timing flake; must be deterministic before xdist), Bean 0154 (temp-name fuzz flake;
  per-worker temp dirs help), Bean 0152 (smaller modules).

## Progress (2026-10-28)

PR #99 (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/99) completed the review loop and Stage 5, and
awaits the maintainer's merge.

- Review loop: 8 iterations. Every finding was applied (none rejected): the cwd-dependent git-config test that failed
  CI, the reordered `intents.jsonl` row, environment-injected git config, the wall-clock latency benchmark that failed
  under xdist (now thread CPU time with the 50 ms limit kept), spelling, the `unittest` wording, and PR body and
  execution-note accuracy. 3/3 ensemble approval at `de66397`, posted as review 5680741325 (COMMENT, own PR).
- Stage 5: `holon calibrate` predicted EV 28.44, actual 53.42 (ΔEV +24.98). `/calibrated` pushed, fast-forwarded into
  the PR head, then `6e9df1d` formatted the generated report (Bean 0162 defect recurred). All 10 checks pass.
- Real CI, job total / pytest time, main `fbd3b35` → `8925e19`: unit macOS 404 / 382.4 s → 178 / 153.1 s; unit ubuntu
  251 / 241.8 s → 136 / 123.4 s; Workspace survival 430 / 417.0 s → 273 / 257.7 s.
- Follow-ups logged: Bean 0176 (pytest only), Bean 0177 (architecture research).
