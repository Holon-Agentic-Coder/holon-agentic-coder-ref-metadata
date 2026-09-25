---
# holon-agentic-coder-ref-metadata-0050
title: "Verify and assert the jq prerequisite for the sandbox credential path"
status: todo
type: task
priority: normal
tags:
  - sandbox-executor
  - prerequisites
  - credentials
  - docker
  - agent-runner
created_at: 2026-09-26T16:40:00Z
updated_at: 2026-09-26T16:40:00Z
---

`jq` is a hard runtime prerequisite for agent credential delivery inside the sandbox, but nothing asserts it. The one
place that depends on it degrades silently, so a missing `jq` surfaces as an unrelated "missing API key" failure later
in the run.

## Context and measured evidence (2026-09-26)

Audited every `jq` reference in the harness and both target repositories:

| Site                                                       | Kind of `jq` use                                | Guarded?                    |
| ---------------------------------------------------------- | ----------------------------------------------- | --------------------------- |
| `apps/sandbox-executor/entrypoint/role_dispatcher.sh:7-20` | bare `jq -r` binary, extracts the secret bundle | yes, `command -v jq`        |
| `.agents/skills/clean_branches/SKILL.md:270`               | `gh ... --jq` (gh's built-in Go filter)         | n/a -- needs no host binary |
| `.agents/skills/pr_review_resolver/SKILL.md:44`            | `gh ... --jq`                                   | n/a -- needs no host binary |

So the skills do **not** depend on a host `jq`, and the only real dependency is the container entrypoint. That
dependency is currently satisfied:

- `apps/sandbox-executor/Dockerfile:11` installs it:
  `apt-get install -y --no-install-recommends git curl jq build-essential ca-certificates ssh vim`
- Live images checked: `holon/base` -> `jq-1.7`, `holon/agent-antigravity` -> `jq-1.7`, `holon/orchestrator` -> `jq-1.7`

## The defect: correct today, silent tomorrow

`role_dispatcher.sh` guards the whole block with `if [ -f "$SECRET_BUNDLE" ] && command -v jq &>/dev/null; then`. The
guard is what makes this undeletable-but-invisible: if `jq` ever disappears from the image (base image change, a slimmed
apt layer, a custom agent image that skips the package), the entire credential-extraction block is skipped **without a
single line on stderr**. `HOLON_AGENT_KEY` is then never exported and the run dies much later inside
`AgentRunner.validate()` with `Please set 'HOLON_AGENT_KEY' ...` -- which points at the host environment, not at the
real cause, and is indistinguishable from a genuinely missing key. This is the same diagnostic black hole Bean 0049 hit
when the sandbox could not reach a host-local provider.

Two further sharp edges in the same block:

1. The script runs under `set -euo pipefail`. A malformed or truncated secret bundle makes `jq -r` exit non-zero, which
   aborts the entrypoint for **every** role with no message at all.
2. There is no build-time or CI assertion that the image actually ships `jq`. `make build-images` and
   `tests/test_build_all_images.py` verify images build and run, not that their prerequisite tooling exists, so a
   regression would only be discovered as a mysterious agent-auth failure in a live flow run.

## Goals & Action Plan

1. **Make the missing-`jq` case loud instead of silent**: when `$SECRET_BUNDLE` exists but `jq` is unavailable, emit a
   stderr diagnostic on the existing `_holon_ca_log` pattern (that section already models the right behaviour:
   non-fatal, always reported) naming the bundle path, the fact that credentials will not be delivered, and the
   resulting symptom the operator will see downstream.
2. **Stop letting `jq` abort the entrypoint**: make each `jq` invocation failure-tolerant (explicit exit-code check or
   `|| true` with a diagnostic) so a malformed bundle degrades to "no key from bundle" rather than killing intent, plan
   and execution roles alike.
3. **Assert the prerequisite where it is guaranteed**: add a build-time check to the image build (`Dockerfile` smoke
   step or the `make build-images` target) and a case in `apps/sandbox-executor/tests/test_build_all_images.py`
   asserting `jq --version` succeeds in the built image, alongside the existing image checks.
4. **Document it**: record `jq` as a sandbox image prerequisite (not a host prerequisite) in the same place
   `docs/executor/agent_credentials_requirements.md` documents credential requirements, and state explicitly that skill
   usage of `gh --jq` requires no host `jq`, so nobody "fixes" this by adding a host dependency check.

## Acceptance Criteria

- [ ] With `HOLON_SECRET_BUNDLE_PATH` pointing at an existing file and `jq` absent from `PATH`, the entrypoint prints
      one actionable stderr warning naming the bundle path and the downstream symptom, then continues to `exec` the
      role.
- [ ] A malformed/truncated secret bundle no longer aborts the entrypoint under `set -euo pipefail`; the run continues
      without a bundle-derived key and says so on stderr.
- [ ] A test asserts `jq` is present and functional in the built sandbox image (and is skipped, not silently absent, if
      image tests are deselected).
- [ ] Existing behaviour is preserved: a valid bundle still exports `HOLON_AGENT_KEY` and the vendor mapping
      (`AGY_USER_TOKEN`, `ANTHROPIC_API_KEY`, `PI_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENCODE_API_KEY`) is
      unchanged, with agent-id matching (`BUNDLE_AGENT_ID` vs `TARGET_AGENT_ID`) intact.
- [ ] `docs/executor/agent_credentials_requirements.md` names `jq` as a container-side prerequisite and notes that
      `gh --jq` needs no host binary.
- [ ] Suites stay green under `uv run pytest -m "not integration_test"`, plus `uv run ruff check .` /
      `ruff format --check .`.

## Notes

- Target repository: `apps/holon-agentic-coder/` -- `apps/sandbox-executor/entrypoint/role_dispatcher.sh`,
  `apps/sandbox-executor/Dockerfile`, `apps/sandbox-executor/tests/test_build_all_images.py`,
  `docs/executor/agent_credentials_requirements.md`.
- **Must run through the Holon flow**: this edits the target repository, so it needs its own `I-.../P-.../E-...` cycle
  rather than a host-side worktree edit -- see the "Sole Change Path: The Holon Flow" section of `AGENTS.md`.
- Related: Bean 0032 (standardized prerequisite checks for docker/uv/npx -- extend that pattern rather than inventing a
  second one), Bean 0049 (keyless/credential validation asymmetry in `AgentRunner.validate()`, the downstream symptom
  this bean makes diagnosable), Bean 0019 (silent-failure class of defect; execution records with no diagnostics).
