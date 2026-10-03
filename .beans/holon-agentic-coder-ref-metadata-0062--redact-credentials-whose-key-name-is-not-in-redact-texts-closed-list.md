---
# holon-agentic-coder-ref-metadata-0062
title: "Redact credentials whose key name is not in redact_text's closed list"
status: todo
type: bug
priority: normal
tags:
  - redaction
  - secrets
  - sandbox-executor
  - security
created_at: 2026-09-30T04:30:00Z
updated_at: 2026-09-30T11:40:00Z
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

Open.
