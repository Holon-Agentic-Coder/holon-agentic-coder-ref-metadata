---
# holon-agentic-coder-ref-metadata-0086
title: "Extend the unusable-tool rule to the Docker and buildx probes in check-docker"
status: completed
type: task
priority: medium
tags:
  - makefile
  - prerequisites
  - holon-agentic-coder
created_at: 2026-10-11T02:00:00Z
updated_at: 2026-10-12T18:40:00Z
---

## Summary

PR #69 (Bean 0079) established that `command -v <tool>` answers only "is there something with this name". A binary that
exists but fails its own version probe - a crashed wrapper, a half-installed package, a PATH entry shadowing the real
install - was reported as `✅ Found:` with an empty version, and a prerequisite gate that says "all prerequisites are
satisfied" on a machine where the tools do not run is worse than no gate.

By the end of the PR the rule is applied to every probe in `check-prerequisites`: `uv`, `npx`, `gh` and `openssl` all
treat an empty version string as unusable (fatal for uv/gh/openssl, warning for npx), each pinned by a test, each proven
non-vacuous by mutation. `GNU Make` was already safe because it greps its version output for the string `GNU Make`
instead of trusting presence.

What is left is in `check-docker`, which this PR's intent did not touch and which stayed out of scope deliberately:
`DOCKER_VER=$$(docker --version 2>/dev/null)` and `BUILDX_VER=$$(docker buildx version 2>/dev/null)` (and the second
buildx capture in the install path) print whatever they get, so a docker CLI that exists but cannot answer prints a
green tick with an empty version. Everything downstream degrades to warnings today, so the worst case is a misleading
line rather than a false green - which is why this is medium and not high.

## Scope

- `check-docker` in `holon-agentic-coder`'s `Makefile`: treat an empty version capture as unusable for the docker CLI
  (fatal path) and for buildx (its existing severity), matching the wording already used by `check-prerequisites`
  (`Unusable: <tool> is on PATH but ...`).
- Tests in `apps/sandbox-executor/tests/test_makefile.py`: the fixture needs a docker factory mirroring `mock_uv` /
  `mock_gh`, so a present-but-unusable docker and buildx are expressible. Every new assertion proven non-vacuous by
  mutation before the commit.
- Daemon-status probing (`docker info`) is out of scope: a running daemon is a different question from a working binary,
  and it already has its own branch.

## Origin

Found while reviewing PR #69 (Bean 0079), iteration 4, where the same defect surfaced in three successive rounds - first
`gh`/`openssl`, then `uv`, then `npx`. Rather than keep discovering it one probe per review pass, `check-prerequisites`
was closed out completely and this residue was recorded here so the diff stayed inside the approved intent.

## Resolution

Executed as part of a batched Holon flow together with Bean 0083 on `holon-agentic-coder`:

- **Intent**: `I-1791787565-calibration-merge-base-and-docker-probe-unusable/_`
- **Plan**:
  `I-1791787565-calibration-merge-base-and-docker-probe-unusable/P-1791787590-antigravity-agent-gemini-3.8-flash-medium/_`
- **Execute**:
  `I-1791787565-calibration-merge-base-and-docker-probe-unusable/P-1791787590-antigravity-agent-gemini-3.8-flash-medium/E-1791788331-antigravity-agent-gemini-3.8-flash-medium/_`
- **Implementation**: Updated `Makefile` `check-docker` target to detect empty version captures from `docker` CLI and
  `docker buildx` as unusable, and added comprehensive pytest coverage in
  `apps/sandbox-executor/tests/test_makefile.py`.
- **Pull Request**: [PR #70](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/70)
- **Review Loop**: 3-agent ensemble review passed with unanimous `APPROVED` verdict; 10/10 GitHub Actions CI checks
  passed.
- **Stage 5 (Calibration)**: Calibrated pre-merge on execution branch with calibrated branch pushed.
- **Merged**: PR #70 merged into `origin/main` on 2026-10-12 (merge commit `5214e6f763e94ce54459e224e6a78d989f4a80b6`).
