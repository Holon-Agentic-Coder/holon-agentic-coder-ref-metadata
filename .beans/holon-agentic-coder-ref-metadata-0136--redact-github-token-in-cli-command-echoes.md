---
# holon-agentic-coder-ref-metadata-0136
title: "Host CLI logs the GitHub token in plaintext in clone and docker command lines"
status: completed
type: bug
priority: high
tags:
  - security
  - credentials
  - cli
  - redaction
  - logs
created_at: 2026-10-22T02:40:00Z
updated_at: 2026-10-26T02:33:21Z
---

## Problem

The host-side Holon CLI prints a live GitHub credential in clear text on stdout, twice, on every `holon plan` /
`holon execute` invocation:

1. The composed container environment is echoed, including `GITHUB_TOKEN=<token>` and
   `HOLON_REPO_URL=https://x-access-token:<token>@github.com/<org>/<repo>.git`.
2. The in-sandbox git helper echoes the clone command it is about to run, with the token embedded in the URL:

```text
Running: git clone --branch I-... --single-branch --depth 1 https://x-access-token:gho_***@github.com/...
```

This was captured on 2026-10-22 in ordinary operator output (`holon plan` log), i.e. with no debug flag and no
`--verbose`. The exposure surface is therefore: the terminal scrollback, any `tee`/CI log of a flow run, every captured
run artifact under `.subagent/`, and any agent transcript that reads such a log. `redact_text()` exists in
`sandbox_executor/entrypoint/executor.py` and is applied to ledger records and wire logs, but not to these echoes.

Note the surrounding code is otherwise careful about secrets (Bean 0062 and Bean 0073 redaction work, wire-log
scrubbing, `Pki`/wire-log file permissions in Bean 0070), which makes these two echoes an inconsistency rather than a
design choice.

## Scope

- Redact every credential that is interpolated into a printed command or environment echo: `GITHUB_TOKEN`, `GH_TOKEN`,
  the `user:token@host` userinfo component of any URL (including `HOLON_REPO_URL`), and `HOLON_MITM_WEB_PASSWORD` /
  mitmweb `?token=` values. Reuse the existing `redact_text()` helper (or a shared `redact_command()` in
  `sandbox_executor/git.py`) rather than adding a second pattern set.
- Prefer passing the token to the container through a file or `--env-file` with `0600` permissions over `-e KEY=value`
  on the command line, so the value stops appearing in the process arguments that `docker run` builds.
- Store the clone URL without embedded credentials and supply the token via a git credential helper or a
  `url.<base>.insteadOf` rewrite generated inside the container.
- Add tests asserting that (a) a composed `docker run` command string and (b) a printed clone command, when a token is
  present in the environment, contain no substring of the token value, and (c) the printed line still identifies the
  repository and branch it refers to.
- Add a pre-commit / CI hygiene grep for `x-access-token:` and `ghp_`/`gho_` patterns in tracked files and in generated
  artifacts that the harness commits.

## Acceptance criteria

- Running `holon plan` / `holon execute` with a token present emits no credential material on stdout/stderr.
- `uv run pytest` passes, including the new no-leak assertions.
- Existing redaction behaviour for ledger and wire-log records is unchanged.

## Containment status (2026-10-22) -- maintainer action DONE, code fix outstanding

- **Rotated.** The credential was refreshed by the maintainer through `gh auth refresh` (device flow). Agents cannot do
  this step: it needs a real TTY, a browser and the keyring. A pty driver stalls on the OSC-11 background-colour query
  before gh ever prints the one-time code, so this stays a human action.
- **Supersession verified.** The value that was printed on 2026-10-22 now fails with `HTTP 401` /
  `{"message":"Bad credentials"}` against `GET /user`, while the current token authenticates normally (`gh api user`
  resolves the account and the core rate limit reads 4998/5000). The stored credential record was rewritten the same
  day, and the `/tmp` log copies have been scrubbed.
- **Scopes were NOT reduced.** `gh auth refresh` keeps previously added scopes when none are specified, so the
  credential still carries `admin:public_key`, which no flow stage needs. Optional hardening at the next refresh:
  `gh auth refresh --scopes repo,read:org,gist` (add `workflow` only if a flow must push `.github/`).
- **Why this bean stays open:** rotation is containment only. Until the echoes are redacted, every `holon plan` /
  `holon execute` run discloses the _current_ token, so the exposure reopens on the first run and the same rotation
  cycle repeats.

## Source

Captured 2026-10-22 in `/tmp/s2_plan_pi.log` (since scrubbed) while running Stage 2 of Bean 0132 on
`holon-agentic-coder`.

## Resolution

- **Pull Request**:
  [Holon-Agentic-Coder/holon-agentic-coder#96](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/96)
- **5-Stage Provenance**:
  - Intent: `I-1792815987-redact-github-token-in-cli-echoes-v2/_`
  - Plan: `P-1792815994-claude-agent-claude-opus-5-5`
  - Execution: `E-1792816376-claude-agent-claude-opus-5-5`
  - Review: 3-agent ensemble consensus `APPROVED` (3/3), first at `f1117d3` (review 5637034878). After merging `main`
    (#90, #93) it went through iterations 4–21 and was re-posted at `cf2c405` (review 5637983463).
  - Calibration: report `a3320e6` plus Bean 0146 annotation `08c0ee3` (Predicted EV 2.36 from the wrong row; Overall
    15.73 | Actual EV 3.84).
- **CI Status**: 10/10 passing, CodeQL 0 open alerts. Merged by the maintainer on 2026-10-24 as `fbabb3a`.
- **Supersedes** PR #92 (closed). #92's plan ID collided with #91's (`P-1792765112`), so the bean was re-run under a
  fresh plan (see Bean 0149).
- **Outcome**:
  - There is now a canonical `sandbox_executor/redaction.py`.
  - Credentials are kept off the docker argv, for the main run and the pre-flight probe, by a 0600 env-file.
  - Every top-level CLI handler goes through `redact_cli_error`.
  - Messages about URL-valued config show only a validated host or the variable name, enforced by
    `tests/test_url_message_fuzz.py`.
  - The pre-flight argv leak that #93 introduced is fixed.
- **Follow-ups**: Bean 0148 (#90 `CredentialRedactor` gaps and `error_context`), Bean 0154 (flaky fuzz leak check), Bean
  0155 (general `HOLON_*` forwarding on the argv).
