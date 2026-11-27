---
# holon-agentic-coder-ref-metadata-0633
title: "Squash merges add Co-authored-by agent trailers and Coherence lacks hook setup"
status: in-progress
type: bug
priority: normal
tags:
  - harness
  - git
  - ci
  - holon-coherence
  - holon-agentic-coder
created_at: 2026-11-27T12:11:44Z
updated_at: 2026-11-27T17:35:04Z
---

## Notes

### Evidence (2026-11-27 fifth-merge Coherence audit, `4a02926b`)

- Even after [holon-coherence#78](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/78) (`010ffa26`, Bean
  `0567`) added `scripts/check_commit_trailers.py`, `.githooks/commit-msg`, and
  `.github/workflows/test-commit-trailers.yml`:
  1. All 5 subsequent squash-merge commits on `holon-coherence/main` (`010ffa2`, `0491b55`, `827e15a`, `ffb4804`,
     `4a02926b`) and recent squash merges on `holon-agentic-coder/main` (`2a83e4cc7`, `b366a559e`) still carry 5
     `Co-authored-by: Holon <Role> Agent` trailers on `main`. Because each flow stage commits under a distinct git
     author (`Holon Intent Agent`, `Holon Planner Agent`, `Holon Executor Agent`, `Holon Review Loop Agent`,
     `Holon Calibrate Agent`) without inline trailers, `pull_request` CI passes, and GitHub squash-merge then
     synthesizes `Co-authored-by:` trailers for each commit author onto `main` (which `test-commit-trailers.yml` never
     scans since it triggers only on `pull_request`).
  2. `.agents/scripts/install_git_hooks.py` installs hooks only in the harness repository (not `apps/holon-coherence` or
     `apps/holon-agentic-coder`), and `holon-coherence/Makefile` has no hook-path setup or check wiring
     `.githooks/commit-msg`.
- **Audit update (`2026-11-27T15:46Z`):** All **4** new HAC squash merges (`#415` `bebb0840d`, `#424` `c03385aff`,
  `#425` `da13a83ca`, `#426` `1f3331637`) and all **4** new Coherence squash merges (`#83` `9eddccdc3`, `#67`
  `63a6bf3f7`, `#84` `71d46b44b`, `#85` `4d2cfcf81`) still landed `5` `Co-authored-by: Holon <Role> Agent` trailers each
  on `main`.

### Proposed Change

1. Decide whether flow stage commits use a uniform commit author (with stage/role metadata kept in commit trailers and
   append-only ledgers) or strip `Co-authored-by:` trailers in the squash-merge workflow/instructions, and check `push`
   commits on `main` (or document the squash-author behaviour explicitly in `check_commit_trailers`).
2. Wire `.githooks/` installation (or `core.hooksPath .githooks`) in `holon-coherence` `Makefile` / setup and extend
   `.agents/scripts/install_git_hooks.py` (or target hook checks) so `.githooks/commit-msg` is active automatically.

### Expected Gain & Cost

- Ensures the no-coauthor-trailer invariant holds on `main` history as well as PR branch commits, and activates local
  `commit-msg` enforcement in target checkouts.
- Cost: small (`~30` lines across `Makefile` / `install_git_hooks.py` / flow git-author config or CI workflow).

## Acceptance Criteria

- [ ] Target repository setup (`holon-coherence` `Makefile` and/or `.agents/scripts/install_git_hooks.py`) enables the
      versioned `.githooks/commit-msg` hook automatically in target worktrees.
- [ ] Squash-merged commits on `holon-coherence/main` and `holon-agentic-coder/main` do not introduce unintended
      `Co-authored-by:` agent trailers (verified via `scripts/check_commit_trailers.py` or equivalent check).
- [ ] Automated tests verify hook installation and commit-trailer enforcement under `uv run pytest`.

## Flow

- **Slice 1 (`2026-11-27`, `coherence-install-hooks-setup`):** Adds idempotent `install-hooks` target to
  `holon-coherence` `Makefile` (activating `.githooks/commit-msg` via `git config core.hooksPath .githooks`, supporting
  `DRY_RUN` and `help`) with tests in `tests/test_makefile.py` and `tests/test_check_commit_trailers.py`
  (`todo/intent-0633-coherence-install-hooks-setup.json`, `todo/intent-coverage-0633.json`). Harness
  `.agents/scripts/install_git_hooks.py` wiring and uniform flow commit-author / squash-merge trailer policy are
  deferred to Slice 2.

## Resolution
