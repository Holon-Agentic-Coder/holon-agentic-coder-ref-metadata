---
# holon-agentic-coder-ref-metadata-0249
title: "Replace and completely remove --repo-dir with --target-worktree across Holon CLI"
status: in-progress
type: feature
priority: high
tags:
  - cli
  - ergonomics
  - worktree
  - flags
  - holon-agentic-coder
created_at: 2026-11-07T08:57:00Z
updated_at: 2026-11-07T09:25:00Z
---

## Problem

Currently, Holon CLI commands (`holon flow`, `holon review`, `holon doctor`, `holon calibrate`, etc.) use the legacy
`--repo-dir` flag to specify the location of the repository worktree on disk:

```bash
holon flow /path/to/intent.json --repo-dir apps/holon-agentic-coder/main
```

In our bare-clone and isolated multi-worktree architecture, `--repo-dir` is ambiguous, confusing, and inaccurate:

1. **Confusion with Starting Branch**: Operators frequently confuse `--repo-dir` with a starting Git branch ref (e.g.
   asking whether `--repo-dir` is supposed to specify the starting branch), rather than an anchor directory path on
   disk.
2. **Conceptual Collision with `--target`**: In `holon review` and Stage 4 review loops, `--target` refers to a **Git
   ref or PR number** (e.g. `--target 135` or `--target I-.../P-.../E-.../_`), whereas `--repo-dir` refers to a
   **filesystem working tree**.
3. **Workspace Inaccuracy**: What the operator is actually providing is the **target working tree** (or anchor worktree)
   from which Git remote URLs, ledgers, and branches are derived and from which dedicated feature worktrees are
   provisioned.

Because Holon is pre-release software currently undergoing active bootstrap, **backwards compatibility is explicitly not
required**. The legacy `--repo-dir` flag, variable names, and environment variables should be completely retired and
removed rather than aliased.

## Goal

Completely replace and remove `--repo-dir` across the entire codebase with `--target-worktree`, retiring all legacy
aliases and parameter names.

### 1. Canonical Flag in `cli/options.py`

In `apps/sandbox-executor/src/sandbox_executor/cli/options.py`:

- Replace `add_repo_dir_option` with `add_target_worktree_option`:

```python
def add_target_worktree_option(
    parser: argparse.ArgumentParser,
    default: str | None = None,
    help: str = "Target repository worktree path (default: current directory).",
) -> None:
    """Add standard --target-worktree argument to a parser."""
    parser.add_argument(
        "--target-worktree",
        dest="target_worktree",
        default=default,
        help=help,
    )
```

- Do **not** register `--repo-dir` as an alias. Invoking `--repo-dir` must result in an unrecognized argument error.

### 2. Update All CLI Subcommands & Dispatchers

Update all subcommand parsers and execution handlers across:

- `apps/sandbox-executor/src/sandbox_executor/cli/commands/flow.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/calibrate.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/consult.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/doctor.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/ledger.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/promote.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/reconcile.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/record.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/review.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/stats.py`
- `apps/sandbox-executor/src/sandbox_executor/cli/commands/veto.py`

All command handlers must expect and read `args.target_worktree`.

### 3. Context & Engine Clean Refactor

In `apps/sandbox-executor/src/sandbox_executor/flow.py`:

- Rename `FlowContext.repo_dir` to `FlowContext.target_worktree`.
- In `agent_runner.py`, `turns.py`, `calibration.py`, and `git_flow.py`:
  - Rename `repo_dir` parameters and local variables to `target_worktree`.
  - Replace `HOLON_REPO_DIR` environment variable with `HOLON_TARGET_WORKTREE`.

### 4. Documentation & Help Text Alignment

- Update `--help` descriptions across all CLI commands to display `--target-worktree`.
- Update relevant user guides in `docs/` and examples to use `--target-worktree`.

### 5. Hermetic Unit Tests (Minimise Mocking)

In `apps/sandbox-executor/tests/test_cli_options.py` and `tests/test_flow.py`:

- Test that passing `--target-worktree /some/path` populates the worktree path correctly.
- Test that `--repo-dir` is rejected as an unrecognized argument (asserting clean removal).
- Update all existing test fixtures to pass `--target-worktree` instead of `--repo-dir`.
- Strictly minimise mocks and test against real `argparse` instances and real Git worktrees.

## Constraints

- Complete removal: no backward-compatibility shims, aliases, or fallback mappings for `--repo-dir`.
- Australian English spelling in all documentation and code comments.
- Zero new external dependencies; dependencies managed strictly via `uv`.
- All tests executed strictly via `uv run pytest`.
- Linting and documentation gates (`uv run task check` or `make lint`) must pass cleanly.
- Target repository isolation: zero harness path leaks into `holon-agentic-coder`.
- Merge remains human-only.
