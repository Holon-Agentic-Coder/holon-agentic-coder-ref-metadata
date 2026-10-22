---
# holon-agentic-coder-ref-metadata-0136
title: "Host CLI logs the GitHub token in plaintext in clone and docker command lines"
status: todo
type: bug
priority: high
tags:
  - security
  - credentials
  - cli
  - redaction
  - logs
created_at: 2026-10-22T02:40:00Z
updated_at: 2026-10-22T02:40:00Z
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

## Immediate action for the maintainer (not a code change)

The token that was printed on 2026-10-22 (`gho_...`, GitHub OAuth token used by `gh` on this host) should be treated as
disclosed to local logs and agent transcripts and **rotated**: `gh auth refresh-token` (or revoke the OAuth grant at
<https://github.com/settings/applications>) and then re-run `gh auth login`. Local log copies under `/tmp` have already
been scrubbed; rotation is the only real remediation.

## Source

Captured 2026-10-22 in `/tmp/s2_plan_pi.log` (since scrubbed) while running Stage 2 of Bean 0132 on
`holon-agentic-coder`.
