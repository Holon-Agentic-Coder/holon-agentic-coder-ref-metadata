---
# holon-agentic-coder-ref-metadata-0377
title: "Rename the *_fuzz tests after what they protect, make their random secrets reproducible, fix the flaky case"
status: completed
type: bug
priority: high
tags:
  - tests
  - flaky
  - security
  - redaction
  - holon-agentic-coder
created_at: 2026-11-23T08:45:00Z
updated_at: 2026-11-23T11:40:00Z
---

## Problem

`apps/sandbox-executor/tests/test_url_message_fuzz.py` (906 lines, added by PR #96 on 2026-10-24) fails intermittently
and has blocked unrelated pull requests three times in one day (2026-11-23): PR #244 (stress run), PR #247 (unit) and PR
#254 (`unit (macos-latest)`). The earlier failures were in
`test_invalid_envelope_value_never_echoed_by_doctor_or_run_path` (about 2 of 2,480 cases, `HOLON_TURN_TIMEOUT_SECONDS`).
On PR #254 the failed log shows the file's tests at about twice their usual duration (for example 29.8 s against 15.0
s); which assertion failed there is not yet confirmed.

Two defects in the tests themselves:

1. **The names say nothing about the code under test** (maintainer, 2026-11-23). `test_url_message_fuzz.py` checks that
   no message built from a URL-valued setting (proxy URL, local model base URL, gateway URL) echoes any 4-character
   fragment of the credential in it, across every entry point (warnings, errors, exception text, log lines,
   `holon doctor` text and `--json`, the gateway probe, Docker argv and env files). "fuzz" names the technique, loosely:
   it is a fixed shape matrix (5 prefixes x 6 host forms x 3 suffixes x credential shapes), not a Hypothesis property
   test. Its sibling `test_config_fuzz.py` (malformed `models.json` and settings never crash `holon doctor` or the run
   path) has the same naming problem.
2. **The secrets are random and unseeded.** Both files build credentials with `secrets.choice` on every run
   (`test_url_message_fuzz.py:60,65`, `test_config_fuzz.py:41`), so a failing case cannot be reproduced: no seed is
   printed, and failure messages deliberately name only the case id. A random credential can collide with ordinary
   output or a temp path; the module docstring already masks two such collisions (the `mkstemp` env-file path and the
   `mkdtemp` pi-agent dir), which suggests a third is still unmasked.

## Goal

1. **Names state the subject.** Rename the files and their test functions after what they protect, for example
   `test_url_credential_redaction.py` and `test_malformed_config_never_crashes.py`, and update every reference (CI
   configuration, timing baselines, slow-test lists, docs). No test is dropped or weakened.
2. **Reproducible inputs.** Credentials come from a seeded generator: a fixed default seed in CI, overridable by an
   environment variable for exploratory runs, and the seed and the failing case id are printed on failure. A stress mode
   can still vary the seed across runs.
3. **Find and fix the flaky case.** Reproduce the intermittent failure with a seed sweep (the stress job), identify the
   collision or timing dependency (`HOLON_TURN_TIMEOUT_SECONDS` in the envelope cases, or a wall-clock limit on a slow
   macOS runner), and fix the cause: mask the colliding text, change the credential alphabet, or remove the timing
   dependence. Do not fix it by retrying or loosening the 4-character leak check.
4. **A flaky test is not a red PR.** If the failure on PR #254 is a duration threshold, the timing comparison reports a
   finding without failing the unit job, or uses a tolerance suited to the macOS runners.

## Acceptance criteria

- The two files and their tests are renamed; a repository search finds no `_fuzz` test name left, and CI and timing
  baselines use the new names.
- Running the suite twice with the same seed produces the same credentials; a failure prints the seed and case id.
- A seed sweep of at least 200 runs of the renamed URL-redaction test passes on Ubuntu and macOS.
- The root cause of the intermittent failure is stated in the PR with the seed that reproduces it before the fix.
- All tests pass via `uv run pytest`; `uv run task lint` and `uv run task lint-docs` pass.

## Touch set

`apps/sandbox-executor/tests/test_url_message_fuzz.py`, `apps/sandbox-executor/tests/test_config_fuzz.py` (both
renamed), a shared seeded-secret helper in the tests. A search of the repository (outside the ledgers, plans and
execution records) found no other file naming them, so the rename should need no CI or baseline edits; the flow confirms
this.

## Related

Noted as "not yet a bean" in the 2026-11-23 queue notes. Blocks nothing, but it keeps failing unrelated PRs; with the
merged-head CI gate (PR #250) a flaky failure on a merged head withdraws an approval and restarts Stage 4.

## Resolution

Delivered via [PR #261](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/261) and merged into `main`
(`7ab455c`):

- **Root cause of the flaky case**: in the forwarded invalid-value cases (`HOLON_TURN_TIMEOUT_SECONDS`,
  `HOLON_STAGE_BUDGET_SECONDS`) the run creates the pi-agent session dir with
  `tempfile.mkdtemp(prefix="holon-pi-agent-")`. Its 8 random characters (and the per-run `pytest-<N>` path) are mounted
  and echoed; when 4 of them equal a 4-character run of the case's random credential, the leak check reports a false
  leak twice for one case. The #244 mask over the whole pi-agent path had been hiding this. Product code does not leak.
- **Reproducing seed (before the fix)**: `CREDENTIAL_TEST_SEED=211`, case
  `env:HOLON_TURN_TIMEOUT_SECONDS/socks5/user-password/digits6-colon/ipv4/path` (fragment `jvzq` in
  `holon-pi-agent-w6tcjvzq`); seed 227 is a second reproducer (`gvzj`).
- **Key Architectural Deliverables**: `test_url_message_fuzz.py` renamed to `test_url_credential_redaction.py` and
  `test_config_fuzz.py` to `test_malformed_config_never_crashes.py`, with the matching test-function renames; all 79
  baseline tests kept (one regression test added, 80); every credential and fallback temp name drawn from the new
  `tests/seeded_secrets.py` (default seed 0, `CREDENTIAL_TEST_SEED=<n>` to reproduce, `random` for stress); failure
  messages print the seed and case ids. No retry, rerun or loosened 4-character check.
- **Verification & Tests**: seed sweep 1000..1199 (200 of 200 passed); deterministic test for the HOME-prefix sharing
  case; `ruff` checks pass.
- **Holon Flow Traversal**: intent, plan, execute, review loop and calibration completed (execution record
  `E-1795425615-CLA-CO5.5`).

## Progress

- 2026-11-23: flow `name-and-seed-redaction-tests` merged as PR #261 (merged by the maintainer, 11:36 UTC). Stages on
  claude-agent/claude-opus-5-5: intent ok, plan ok, execute ok (102.7 min), review approved (iteration 1 nit
  FIND-R1-001-01, PR body lacked root cause and seed), calibrate ok; final head CI green.
- Root cause: the forwarded invalid-value cases create a `holon-pi-agent-<random>` dir under the isolated HOME; when 4
  characters of its random name match a 4-character run of the case credential, the leak check reports a false leak.
- Reproducing seed: `CREDENTIAL_TEST_SEED=211` (case
  `env:HOLON_TURN_TIMEOUT_SECONDS/socks5/user-password/digits6-colon/ipv4/path`, fragment `jvzq`); seed 227 is a second
  one. Sweep: seeds 1000..1199, 200 of 200 passed.
- Gap: the PR body does not state the root cause or the seed the intent requires; they are only in
  `executions/E-1795425615-CLA-CO5.5.md`.
