---
# holon-agentic-coder-ref-metadata-0062
title: "Redact credentials whose key name is not in redact_text's closed list"
status: completed
type: bug
priority: normal
tags:
  - redaction
  - secrets
  - sandbox-executor
  - security
created_at: 2026-09-30T04:30:00Z
updated_at: 2026-10-05T23:12:00Z
---

`redact_text` in `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` masks a credential only when it can
see the credential's **key name**, and the accepted key names are a closed alternation (`token`, `access_token`,
`secret`, `password`, `api_key`, `auth`, `bearer`, `_pat`, `_key`, `-key`, `secret_key`, `private_key`, `signing_key`,
`encryption_key`, …). A secret printed under any other name is committed verbatim to the execution record and the ledger
row. This is not a truncation bug and it is not new: it is the behaviour of `main`, independent of any byte cut.

Measured on `main` at PR #61 iteration 8, with no byte cut involved at all:

```console
$ .venv/bin/python -c 'redact_text("key   = Zk9mQ7vR2xLp4tYb8nJd3wC6sH5a")'
'key   = Zk9mQ7vR2xLp4tYb8nJd3wC6sH5a'      # unmasked
$ .venv/bin/python -c 'redact_text("api_key   = Zk9mQ7vR2xLp4tYb8nJd3wC6sH5a")'
'api_key=*******'                            # masked
```

The witness class is ordinary: `key = …`, `pwd = …`, `client_secret`, `db_password`, provider SDK names outside the
list, and YAML/JSON dumps whose keys are whatever the called service chose. Agent output is precisely the artifact where
those appear.

Second, narrower gap in the same family: the URL-query rule's anchor is `[?&](token|api_key|…)[^=]*=`, and `[^=]*`
matches newlines, so the anchor prefix can sit lines above a `=`-adjacent value. PR #61's line-boundary fix documents
this as its residual rather than pretending it away.

Third witness, found on PR #61 iteration 12 and the sharpest of the three — the separator does not merely _reach_ a
far-away key name, it can **swallow the next line's key name and use it as the value**, destroying the real anchor:

```console
$ .venv/bin/python -c 'redact_text("cfg:\n  secret:\n    api_key: \'<cred>\'\n")'
cfg:
  secret:
    ******* '<cred>'          # the key NAME is masked, the credential is committed verbatim
$ .venv/bin/python -c 'redact_text("    api_key: \'<cred>\'\n")'
    api_key: '*******'        # the same value on its own line masks correctly
```

`secret:` is in the accepted alternation, its separator `\s*(:\s*|=)\s*` is pure whitespace and therefore crosses the
newline, and the value branch accepts any non-whitespace run — so `api_key` is matched _as the value_ and replaced,
leaving the quoted credential behind. This is worse than an unmatched key name: after the damage the anchor is gone, so
no later redaction pass can recover the value. Measured with **no byte cut at all** (`prepare_agent_output_block` at
budget 60000 reports `truncated: False`), so it is `main` behaviour, out of PR #61's scope by the same attribution rule
that put witness 1 there. Any fix here must treat "the anchor matched the wrong token" as a distinct failure mode from
"no anchor matched", because masking the wrong token is actively destructive.

## Why it is a separate bean and not part of PR #61

The PR #61 review loop ruled both shapes **out of scope** and recorded the ruling in
`apps/holon-agentic-coder/pr61-agent-output-capture/.subagent/holon-agentic-coder_pr61_coordination.json`
(`rejected_suggestions`, `deferred`, item `P-BEAN-1`): PR #61 changes the _ordering_ of bound/redact/refit so that a cut
cannot strand an anchor, and neither of these shapes is caused by a cut. Widening the alternation and adding generic
high-entropy rules were already rejected inside that loop as coverage regressions, so the fix needs its own design pass,
not a diff appended to a redaction-ordering change.

## Notes

- Target repository: `holon-agentic-coder`. Every change to it must go through the five-stage Holon flow
  ([AGENTS.md](../AGENTS.md), "Sole Change Path").
- Any rule added here must survive the adversarial standard the PR #61 loop established: state an invariant, and ship a
  test whose counter-example **must still leak** without it. Six consecutive local heuristics in
  `prepare_agent_output_block` were broken by the next witness; the fixes that held were the structural ones.
- Beware the coverage-vs-secrecy trade-off the loop already hit twice: rules that mask too much destroy the diagnostics
  the record exists to provide (F-IT2-2 dropped retention to 49,987 of 65,536 bytes), and GitHub push protection blocks
  committed vendor-format credential literals, so fixtures must stay synthetic (`tests/test_executor.py::_fake_token`).
- Related: PR #61 (`F-IT4-1` resolution plan rejected the `//2` clamp and generic entropy rules; `F-IT8-1` shipped the
  never-commit-the-region's-first-value-line rule), bean 0019.

## Resolution

Resolved via the complete 5-stage Holon flow in Pull Request
[#64](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/64):

1. **Stage 1 (Intent)**:
   - Created Intent `I-1791190247-redact-credentials-closed-list` and logged to `holon-knowledge/ledger/intents.jsonl`.
   - Pushed branch `I-1791190247-redact-credentials-closed-list/_` to `origin`.

2. **Stage 2 (Plan)**:
   - Generated Plan `P-1791190262-antigravity-agent-gemini-3.8-flash-medium` via containerized `planner-agent`.
   - Logged in `plans.jsonl` and committed plan artifact
     `plans/P-1791190262-antigravity-agent-gemini-3.8-flash-medium.md`.
   - Pushed branch
     `I-1791190247-redact-credentials-closed-list/P-1791190262-antigravity-agent-gemini-3.8-flash-medium/_` to `origin`.

3. **Stage 3 (Execute)**:
   - Executed plan via containerized `executor-agent` (Execution ID:
     `E-1791190583-antigravity-agent-gemini-3.8-flash-medium`).
   - Implemented expanded key alternations, line-scoped URL query parameter anchors, and line-scoped key-value
     separators in `executor.py`.
   - Added adversarial witness tests in `test_executor.py`.
   - Committed and logged execution record `executions/E-1791190583-antigravity-agent-gemini-3.8-flash-medium.md`.
   - Pushed branch `I-1791190247-.../P-1791190262-.../E-1791190583-.../_` to `origin`.

4. **Stage 4 (PR Review Loop)**:
   - Opened PR [#64](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/64).
   - **Iteration 1**:
     - 3-agent ensemble review flagged 2 Critical issues: kebab-case over-masking (`sort-key=asc`) via ASCII `\bkey\b`
       and Branch B multiline newline bleeding swallowing nested quoted keys.
     - Resolver subagent resolved both issues: replaced `\bkey\b` with `(?<![a-zA-Z0-9_-])key\b`, added lookahead
       `(?=[ \t]*(?:,|\n|$))` rejecting colons on the following token, constrained URL parameters with `key(?=[=_-])`,
       preserved delimiter whitespace (`sep = match.group(3)`), and expanded adversarial unit tests.
     - Pushed fix commit `867d8c6` to `origin`.
   - **Iteration 2**:
     - 3-agent ensemble review achieved unanimous approval: Reviewer 1 (`APPROVED`), Reviewer 2 (`APPROVED`), Reviewer 3
       (`APPROVED`) (0 Critical, 0 Important, 0 Nits).
     - Posted consolidated consensus approval review to PR #64 on GitHub.

5. **Follow-Up Refinement (Operator Explicit Instruction Exception)**:
   - Per explicit operator instruction, removed unnecessary and unused keys (`NON_SECRET_FLAGS`, `--pwd`,
     `--credential`, `--credentials`, `--db-password`, `--client-secret`, `--key`) from `SECRET_FLAGS` and
     `_is_secret_flag` in `executor.py`.
   - Removed corresponding synthetic CLI argument test cases from `test_executor.py` while keeping all text-based
     witness patterns (`key = ...`, `pwd = ...`, `client_secret = ...`, `db_password = ...`, line-scoped URL queries,
     and multiline YAML nested dictionaries) intact.
   - Pushed commit `f81d3c8` to PR #64 branch.

6. **Conflict Resolution & Main Sync**:
   - Reconciled merge conflict with `origin/main` after PR #65 landed: merged append-only ledger rows (`intents.jsonl`,
     `plans.jsonl`, `executions.jsonl`) in chronological order.
   - Verified clean test suite execution (414 passing unit tests).
   - Committed merge commit `ae65e24` and pushed to PR #64 branch (`mergeable: MERGEABLE`).

7. **Stage 4 (PR Review Loop — Iteration 4)**:
   - Dry-run review passed with `APPROVED` (0 Critical, 0 Important, 0 Nit).
   - 3-agent ensemble consensus review achieved unanimous approval: Reviewer 1 (`APPROVED`), Reviewer 2 (`APPROVED`),
     Reviewer 3 (`APPROVED`) (0 Critical, 0 Important, 0 Nit; 10/10 CI checks passing).
   - Posted consensus review to PR #64 on GitHub
     ([receipt](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/64#pullrequestreview-5425917675)).

8. **Stage 5 (Calibration)**:
   - Ran `holon calibrate` against the execution branch.
   - Generated calibration report: Predicted EV: `72.60`, Actual EV: `73.86` ($\Delta\text{EV}: +1.26$).
   - Pushed `/calibrated` branch to `origin`: `I-1791190247-.../P-1791190262-.../E-1791190583-.../calibrated`.
   - Committed updated calibration report directly on top of PR #64 branch (`01adf1b`) and pushed to `origin`.

9. **Human-Only Merge Hand-off**:
   - In accordance with the immutable Human-Only PR Merging Invariant, all agent activity ceases upon posting approval
     and pushing calibration. Ready for manual human review and merge at
     https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/64.
