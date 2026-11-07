---
# holon-agentic-coder-ref-metadata-0249
title: "Replace --repo-dir CLI flag with --target-worktree across Holon CLI commands"
status: todo
type: feature
priority: high
tags:
  - cli
  - ergonomics
  - worktree
  - flags
  - holon-agentic-coder
created_at: 2026-11-07T08:57:00Z
updated_at: 2026-11-07T08:57:00Z
---

## Problem

Currently, Holon CLI commands (`holon flow`, `holon review`, `holon doctor`, `holon calibrate`, etc.) use the
`--repo-dir` flag to specify the location of the repository on disk:

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

## Goal

Replace `--repo-dir` with `--target-worktree` as the canonical flag across all Holon CLI commands, while preserving
`--repo-dir` as a backward-compatible alias.

### 1. Canonical Flag in `cli/options.py`

In `apps/sandbox-executor/src/sandbox_executor/cli/options.py`:

- Update `add_repo_dir_option` (and alias/rename to `add_target_worktree_option`):

```python
def add_target_worktree_option(
    parser: argparse.ArgumentParser,
    default: str | None = None,
    help: str = "Target repository worktree path (default: current directory).",
) -> None:
    """Add standard --target-worktree (and backward-compatible --repo-dir) argument to a parser."""
    parser.add_argument(
        "--target-worktree",
        "--repo-dir",
        dest="target_worktree",
        default=default,
        help=help,
    )
```

- Ensure any legacy access via `getattr(args, "repo_dir", ...)` continues to resolve cleanly by mapping or aliasing
  attributes on parsed namespaces.

### 2. Update CLI Commands & Option Parsers

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

Handlers should resolve the worktree path from `args.target_worktree or getattr(args, "repo_dir", None) or "."`.

### 3. Context & Checkpoint Compatibility

In `apps/sandbox-executor/src/sandbox_executor/flow.py` (`FlowContext`):

- Support `target_worktree` as an alias or parameter alongside `repo_dir`.
- Ensure checkpoint JSON serialization and deserialization remain backward-compatible without breaking existing
  checkpoints.

### 4. Documentation & Help Text Alignment

- Update `--help` descriptions across all CLI commands to display `--target-worktree`.
- Update relevant user guides in `docs/` and examples to use `--target-worktree`.

### 5. Hermetic Unit Tests (Minimise Mocking)

In `apps/sandbox-executor/tests/test_cli_options.py` and `tests/test_flow.py`:

- Test that passing `--target-worktree /some/path` populates the worktree path correctly.
- Test that passing the legacy `--repo-dir /some/path` still populates the worktree path identically for backward
  compatibility.
- Test that `--help` displays `--target-worktree` as the canonical option.
- Strictly minimise mocks and test against real `argparse` instances and real Git worktrees.

## Constraints

- Australian English spelling in all documentation and code comments.
- Zero new external dependencies; dependencies managed strictly via `uv`.
- All tests executed strictly via `uv run pytest`.
- Linting and documentation gates (`uv run task check` or `make lint`) must pass cleanly.
- Target repository isolation: zero harness path leaks into `holon-agentic-coder`.
- Merge remains human-only.
