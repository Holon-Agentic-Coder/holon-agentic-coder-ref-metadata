---
# holon-agentic-coder-ref-metadata-0085
title: "Tell the executor to use the baked-in OS toolbelt and add lint / json-lint / yaml-lint targets"
status: completed
type: task
priority: high
tags:
  - agent-instructions
  - sandbox-image
  - lint
  - holon-agentic-coder
created_at: 2026-10-11T00:00:00Z
updated_at: 2026-10-13T02:27:00Z
---

## Summary

Observed repeatedly, in review passes and in the flow's own role agents: instead of using the tools already installed,
agents write throwaway programs to inspect data - `uv run python - <<'PY'` with `import json` to read a ledger row, a
Node snippet to walk a config. The tool they needed was already in the image: `apps/sandbox-executor/Dockerfile` line 10
installs `jq` today. The behaviour is therefore not a missing-capability problem, it is a missing-instruction problem,
compounded by the fact that the repository has **no lint entry points at all**
(`grep -nE '^[a-z0-9-]*lint[a-z0-9-]*:' Makefile` in `holon-agentic-coder` returns nothing), so there is nothing to run
a validation through.

Two halves, one bean:

1. **Instruct the roles to use the baked-in OS toolbelt.** The sandboxed executor/planner agents take their instructions
   from the cloned target repository's `.agents/AGENTS.md`, so that file is the surface to change. Rule to add: probe
   for a tool before writing code (`command -v <tool>`); never write a one-off Python/Node script to read, filter,
   pretty-print, compare or validate JSON/YAML/CSV/text - use `jq` (`jq -r`, `jq -s 'add'`, `jq -e .`,
   `jq -r 'keys[]'`), `yq` for YAML, `grep`/`awk` for line extraction, `diff`/`cmp` for comparison, `gh api --jq` for
   API responses; writing a program is reserved for logic that is committed, tested and maintained; scratch scripts go
   to `/tmp` (sandbox) or `todo/` (host) and are deleted.
2. **Give the toolbelt lint entry points to be used through.** Install the linters in the sandbox image and expose them
   as Make targets, so "validate this" has a canonical command instead of an invented script.

## Scope

- **Front-load every clarifying question, then run unattended (added 2026-10-11 by operator instruction).** Today the
  intent file is accepted with ambiguities intact and the questions surface mid-plan or mid-execution, where the only
  ways to handle them are pausing the pipeline or guessing silently. Both are wrong: a human who has already specified
  the intent should not be interrupted again, and a silent guess destroys the provenance the ledgers exist to record.
  Required shape:
  - The Intent stage becomes the single question gate. `./holon intent <intent.json>` resolves the request into an
    explicit list of every unresolved decision it can find - scope, acceptance criteria, targets, defaults it would
    otherwise invent, risk-tolerant choices - and presents them together, once. `holon-knowledge/ledger/intents.jsonl`
    then records the answers alongside the intent, so the decisions are auditable, not just the diff.
  - An intent carrying unresolved questions is not executable: the CLI reports them and stops before Plan, rather than
    discovering them later.
  - Plan, Execute, Review and Calibrate must never block on a question. If something unanticipated appears downstream,
    the role agent picks the conservative option, records the decision and its rationale in the execution record, and
    states it in the PR description - it does not stop and wait.
  - `holon flow` gains a check that the intent it was handed is fully resolved, so the unattended five-stage run cannot
    stall on an unanswered question.
- `.agents/AGENTS.md` (holon-agentic-coder): add the OS-toolbelt-first rule described above. This is the instruction
  file the containerised role agents actually load.
- **Minimise runtime environment injection (added 2026-10-11 by operator instruction).** Both host-side agents and flow
  role agents habitually prefix single commands with environment surgery -
  `export PATH="/opt/homebrew/Caskroom/ miniforge/base/bin:$PATH" && uv run ruff format .` - on almost every invocation.
  It should be unnecessary, and it costs more than keystrokes:
  - It rewrites the execution environment per command, so two commands in the same session can resolve different
    binaries for the same tool name, which makes a green gate meaningless about which tool actually ran. This is the
    same class of defect that just cost two review iterations on PR #13 (a stub `PATH` that let the host's real
    `openssl` satisfy a "missing openssl" assertion on `unit (ubuntu-latest)`).
  - Non-interactive automation inherits the mutation or silently does not, so "it worked in my shell" stops predicting
    CI.
  - It burns output tokens and log lines on boilerplate instead of results, which is directly counter to the token-
    reduction work this repository exists to measure.
  - Required changes:
    - `apps/sandbox-executor/Dockerfile`: make the toolbelt discoverable through the existing `ENV PATH` line (uv,
      conda, jq and the new linters) so a role agent never needs an inline `export` to run a gate. Verify by running
      each gate from a clean `docker run` shell with no environment additions.
    - `make use-uv` and the conda bootstrap targets: install/link tool binaries into a directory already on `PATH`
      (`~/.local/bin`) so the host case that currently forces the injection - `uv` reachable only inside a conda base
      environment - stops existing. Add a `make tools` target that prints the absolute resolved path and version of
      every tool the gates need, so "which binary ran" is one command to answer instead of an inference.
    - `.agents/AGENTS.md` plus this harness's `.agents/rules.md`: forbid the per-command `export VAR=... &&` prefix
      pattern. Establish the canonical form (`uv run <tool>` or a `make` target, run from the repository root, with no
      inline environment changes), and require that a tool genuinely missing from `PATH` be fixed durably - install it
      where `PATH` already points, or activate the environment once for the session - rather than patched per command.
      Document the one legitimate exception: a deliberately narrowed environment for a test fixture, which must be built
      inside the test and asserted on, never exported into the caller's shell.
- `apps/sandbox-executor/Dockerfile`: add the missing linters to the existing `apt-get install` line (`shellcheck`,
  `yamllint`) plus `yq` (mikefarah static binary, not the Python `yq` alias), keeping the layer and the cache mounts as
  they are. `jq` is already present - do not re-add it.
- `Makefile` (holon-agentic-coder root): add `lint`, `lint-json`, `lint-yaml`, `lint-shell`, `lint-md` and wire `lint`
  into the existing check/CI path. Implementations must themselves be tool calls, not scripts, e.g.
  `lint-json: jq -e . holon-knowledge/ledger/*.jsonl` (JSONL needs a per-line form), `lint-yaml: yq -e 'true' <files>`,
  `lint-shell: shellcheck entrypoint/*.sh holon`, `lint-md: npx prettier --check "**/*.md"`.
- `.github/workflows/*`: run `make lint` in the hygiene job so the check is enforced, not advisory.
- Tests: `apps/sandbox-executor/tests/test_makefile.py` (or the repo's Makefile test home) gains cases asserting the new
  targets exist and that a deliberately malformed JSON/YAML/shell fixture makes the respective target exit non-zero.
- Mirror the rule text in this harness's `.agents/rules.md` - **done directly**, since harness files are outside the
  flow's reach (see the harness exception in `AGENTS.md`).

## Constraints

- These are `holon-agentic-coder` source changes, so they MUST be produced by the five-stage Holon flow (intent -> plan
  -> execute -> pr-review-loop -> calibrate), not hand-authored in a worktree. This bean is the intent's provenance.
- Do not add a linter that needs a language runtime the image does not already have.
- No synthetic fixtures committed beyond the tiny deliberately-broken files the lint tests need, and those must live in
  the test's temp dir, not the repo tree.

## Origin

Direct operator instruction on 2026-10-11, while Bean 0079's review loops were running: "you are consistently making up
your own solutions to do things like javascript scripts, python - change the instructions for executor to rely on baked
in os as much as possibly (e.g. jq when parsing json) - make lint, json lint, yaml lint, etc".

## Resolution

Executed strictly through the 5-stage Holon flow on `holon-agentic-coder`:

- **Stage 1 (Intent)**: `I-1791812918-executor-toolbelt-and-lint-targets/_`
- **Stage 2 (Plan)**:
  `I-1791812918-executor-toolbelt-and-lint-targets/P-1791812932-antigravity-agent-gemini-3.8-flash-medium/_` (Predicted
  EV: 87.49)
- **Stage 3 (Execute)**:
  `I-1791812918-executor-toolbelt-and-lint-targets/P-1791812932-antigravity-agent-gemini-3.8-flash-medium/E-1791816334-antigravity-agent-gemini-3.8-flash-medium/_`
- **Stage 4 (PR Review Loop)**: Raised Pull Request
  [holon-agentic-coder#72](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/72).
  - Iteration 1: 3-agent ensemble identified Prettier failure on deprecated execution markdown file, question validation
    bypasses in `flow.py`, unpinned `yq` releases, and `%s` escape formatting in Makefile.
  - Resolver: Applied fixes in commit `91642e1` (dropped `executions/` markdown per Bean 0078, fixed question
    validation, pinned `yq` to `v4.44.1`, used `%b` in Makefile printf).
  - Iteration 2: Unanimous 3/3 ensemble approval (`Reviewer 1`, `Reviewer 2`, `Reviewer 3`). All 10 CI checks passed.
- **Stage 5 (Calibration)**: Calibrated pre-merge on branch
  `I-1791812918-executor-toolbelt-and-lint-targets/P-1791812932-antigravity-agent-gemini-3.8-flash-medium/E-1791816334-antigravity-agent-gemini-3.8-flash-medium/calibrated`
  (Predicted EV: 74.44, Actual EV: 74.79, $\Delta EV$: +0.35). Pushed to origin.
- PR #72 is approved and awaiting human merge.
