# Agent Coding Rules & Standards

This document defines the strict rules, styling guidelines, and tool usage constraints that you must follow when writing
code in this repository.

---

## 🎨 Coding Standards

1. **Clean Code**: Write readable, expressive code with descriptive naming conventions.
2. **Error Handling**: Always write defensive code. Handle potential exceptions, null values, and edge cases. Never
   swallow errors silently.
3. **No Placeholders**: Never leave `TODO`, `FIXME`, or placeholder code (e.g., `// implement later`) in code changes
   unless explicitly requested.
4. **Consistency**: Follow the existing indentation, styling, naming conventions (camelCase, snake_case, etc.), and file
   structures of the project.
5. **Documentation**:
   - Update docstrings, READMEs, and inline comments to reflect any changes you make.
   - Maintain the integrity of existing comments that are unrelated to your changes.

---

## 🔧 Tool Usage Constraints

1. **Command Execution**:
   - Always specify the exact `CommandLine` and current working directory (`Cwd`).
   - Never run command strings containing arbitrary, uninspected bash code or scripts from untrusted external URLs.
   - Do not invoke interactive prompts or commands that block indefinitely unless you set appropriate timeouts.
   - **Python & Test Execution**: Always run Python scripts, tests, and CLI tools using `uv` from the repository root
     directory. Never set `Cwd` or `cd` into subpackages (such as `apps/sandbox-executor/`). Never invoke `python3`,
     `pytest`, or `.venv` binaries directly. When generating documentation, scratch scripts, or instructions, ALWAYS
     specify `uv run pytest` (or `uv run <script>`) and NEVER document or generate `PYTHONPATH=...` prefixes or raw
     `python3` invocations.
     - **Unit Test Execution**: Run unit tests using `uv run pytest -m "not integration_test"` from the repository root.
     - **Integration Test Execution**: When running integration tests, first build required container images using
       `./apps/sandbox-executor/build_all_images.sh --output-log`, then run `uv run pytest -m "integration_test"`.
     - **Linting & Lockfile Check**: Validate linting, formatting, and lockfile integrity using: `uv lock --check`,
       `uv run ruff check .`, and `uv run ruff format --check .`.
   - **Single Project `.venv` & Workspace Root Invariant**: Always execute `uv` commands from the repository/project
     root so that virtual environments are maintained solely in the root `.venv`. Never create or initialize nested
     `.venv` directories in subfolders (e.g., `apps/sandbox-executor/.venv`), and never navigate (`Cwd`) into
     subpackages like `apps/sandbox-executor/`, as doing so detaches `uv` from the workspace root Python version
     constraints.
2. **File Editing**:
   - Use `replace_file_content` for a single contiguous block of edits.
   - Use `multi_replace_file_content` for editing multiple non-contiguous blocks in the same file.
   - Never overwrite an entire file with `write_to_file` if you are only making minor edits.
3. **Sandboxing and Security**:
   - Do not attempt to run processes that modify root system directories or execute outside the defined workspace
     directories.
   - If you trigger a permission error, request the minimum required permissions using `ask_permission`.
4. **Path Handling & References**:
   - Never use absolute paths (e.g., starting with `/Users/`, `/home/`, or `file:///Users/`) in any documentation,
     instructions, code comments, tool outputs, or task references.
   - Always refer to files and folders using project-root relative paths (e.g., `.agents/rules.md`) to maintain
     workspace portability across different environments.
5. **Baked-In OS Toolbelt First, Written Scripts Last**:
   - The sandbox image and developer hosts already ship the standard toolbelt. Probe before writing code
     (`command -v <tool>`): `jq` is installed in `apps/sandbox-executor/Dockerfile`, alongside `git`, `curl`, `ssh`,
     `vim`, `build-essential`, plus coreutils, `grep`/`sed`/`awk`, `find`/`xargs`, `sort`/`uniq`/`cut`, `diff`,
     `openssl` and `gh`.
   - **Never write a one-off Python, JavaScript/Node, or other script to read, filter, pretty-print, compare or validate
     JSON, YAML, CSV or plain text.** Use the installed tool instead: `jq -r '.status' f.json`,
     `jq -s 'add' a.json b.json`, `jq -e . f.json` to validate, `jq -r 'keys[]' f.json`; `yq` for YAML; `grep`/`awk` for
     line extraction; `diff`/`cmp` for comparison; `gh api --jq` for API responses.
   - The tell is reaching for `import json`, `json.load`, `require('fs')`, or a `python - <<'PY'` heredoc **to look at
     data**. That is inspection, not implementation: stop and use `jq`.
   - Reserve writing a program for logic that must be committed, tested and maintained. Inspection and verification are
     shell one-liners.
   - When a needed tool is genuinely missing from the image, add it to `apps/sandbox-executor/Dockerfile` and expose it
     through a Makefile target (Bean `0085` tracks the lint toolbelt) rather than substituting an ad-hoc script for it.
   - Scratch scripts, when truly unavoidable, live in the git-ignored scratch area (`todo/` in this harness, `/tmp` in
     the sandbox), never in the repository tree, and are deleted when the check is done.
6. **Universal Agent Credentials (`HOLON_AGENT_KEY`)**:
   - Never use, check, or introduce vendor-specific API key environment variables (such as `GOOGLE_API_KEY`,
     `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AGY_USER_TOKEN`, `PI_API_KEY`) in runner validators, host
     CLI code, or agent configuration logic.
   - Always standardize on `HOLON_AGENT_KEY` across all agents and runner validations. Vendor-specific environment
     variables are mapped exclusively inside container entrypoints (e.g., `role_dispatcher.sh`) from `HOLON_AGENT_KEY`.

---

## 📝 Architectural & Deprecation Directives

1. **Complete Deprecation & Agent Removal**:
   - When dropping support for an agent (such as `open-codex`), remove all references completely across Dockerfiles,
     build matrix targets (`docker-bake.hcl`), Python registries (`agent_runner.py`, `cli.py`), entrypoints
     (`role_dispatcher.sh`), and test suites.
   - Do NOT introduce deprecation fallback stubs, error interception handlers, CLI transition feedback, or legacy
     compatibility shims when dropping an agent unless explicitly requested.
   - Update documentation files by completely stripping all references to the dropped agent rather than adding legacy,
     migration, or deprecation documentation sections.
   - Do NOT generate migration notices, transition guides, or deprecation warnings in release notes or changelogs when
     an agent is dropped.

---

## 🧠 Permanent Engineering Learnings & Invariants

1. **Agent Removal Invariant**:
   - Dropping an agent means total elimination without legacy stubs, CLI deprecation error checks, migration guides, or
     release notes deprecation warnings.

2. **Dynamic Version Resolution Invariant**:
   - Do NOT maintain static hardcoded fallback version maps in code. Dynamic CLI binary execution inside Docker
     containers is the single source of truth. If execution fails, fall back to `"unknown"`.
   - Validate `subprocess.run` exit codes (`result.returncode == 0`) and explicitly catch `subprocess.TimeoutExpired`
     for debug logging clarity.

3. **Empirical Verification Invariant**:
   - Never accept a hypothesized syntax or import failure from a raw LLM diff review without verifying via actual code
     execution (`pytest`, `python3 -c "import ..."`). Unified diff context lines must not be confused with deleted code.

4. **No `PYTHONPATH=...` Command Style & `uv` Enforcement Everywhere**:
   - Never use, execute, or document `PYTHONPATH=... python3` or `PYTHONPATH=... python3 -c` for running scripts,
     testing, inspecting modules, or writing documentation.
   - Always navigate to the target workspace root (`cd apps/holon-agentic-coder/main` or `cd apps/holon-coherence/main`)
     and execute inline Python snippets using `uv run python -c "..."` or test suites using `uv run pytest`.

5. **Strict Repository Separation (Target Codebases vs Metadata)**:
   - `holon-agentic-coder-ref-metadata` is the control plane harness and metadata store
     (`git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref-metadata.git`).
   - `holon-agentic-coder` is the primary fractal intent evolution engine codebase
     (`git@github.com:Holon-Agentic-Coder/holon-agentic-coder.git`), located inside the `apps/holon-agentic-coder/`
     directory.
   - `holon-coherence` is the proxy and optimization gateway codebase
     (`git@github.com:Holon-Agentic-Coder/holon-coherence.git`), located inside the `apps/holon-coherence/` directory.
   - NEVER mix up their git remotes, working directories, commit histories, or task contexts. Commands targeting
     `holon-agentic-coder` or `holon-coherence` must be executed strictly inside their respective directories (or git
     worktrees), and the `origin` remote of `holon-agentic-coder-ref-metadata` must NEVER be altered to point to target
     codebases.

6. **Real API Test Script Invariant (No Pre-Canned Workloads)**:
   - Test scripts designed to hit live LLM provider APIs must NEVER contain hardcoded, pre-canned, or mocked workload
     arrays/dictionaries in source code.
   - Real API test scripts must always accept dynamic user inputs: direct user prompts (`-p` / `--prompt`) or external
     request payload files (`-f` / `--file`).

7. **Explicit API Execution & Key State Invariant**:
   - Never claim or report that a live API test was executed when no API key was supplied by the user.
   - Always declare upfront whether an execution was an offline payload simulation (zero API calls) versus an actual
     live network socket request to upstream provider endpoints.

8. **Holon Flow Sole-Change-Path Invariant (`holon`)**:
   - **All** changes to flow-driven target codebases (`holon-agentic-coder` and `holon-coherence`) MUST be produced
     through the 5-stage Holon flow, spanning the complete lifecycle: Intent -> Plan -> Execute -> PR Review Loop ->
     Calibration. Stage 5 (Calibration) is a **pre-merge** stage: calibrate, then request the human merge.
   - Running `holon` inside either target repository's worktree dynamically resolves `remote.origin.url` via
     `resolve_target_repo_url()`, driving that repository's `holon-knowledge/ledger/` provenance pipeline.
   - Manual stage-by-stage execution (`holon intent`, `holon plan`, `holon execute`, `pr-review-loop`,
     `holon calibrate`) is fully compliant and as compliant as the unified `holon flow <intent.json>` runner, which
     already exists on `main` with a reduced flag set (Bean 0040 tracks the flags and usage docs still outstanding; the
     Bean 0039 pipeline engine is completed). Automation is an optimisation of the flow, never a substitute for any of
     its five stages.
   - **Global CLI Invariant (`holon`)**: Always invoke `holon` directly as an installed CLI tool on `PATH`
     (`holon <subcommand>`), never via relative paths (`./holon`) or repository worktree paths
     (`apps/holon-agentic-coder/.../holon`).
   - The `holon` CLI automatically manages sandbox isolation, credential discovery, SSH agent socket forwarding, branch
     creation (`I-...` Intent, `P-...` Plan, `E-...` Execution, `/calibrated`), and remote pushes to `origin`.
   - Never bypass the flow with manual host-side git or worktree source edits, and never hand-apply a diff because a
     stage failed. A blocked stage means the change is blocked: report the blocker.
   - Per-agent worktrees remain mandatory for harness operation, image builds, code inspection, and verification runs --
     they are explicitly **not** a surface for hand-authoring `holon-agentic-coder` or `holon-coherence` changes outside
     the flow.
   - The sole exceptions are (a) the `holon-agentic-coder-ref-metadata` control plane itself (`.beans/`, `.agents/`,
     `AGENTS.md`), which is edited directly, and (b) an explicit, specific user instruction to edit outside the flow,
     which must be recorded in the commit message and the bean summary.

9. **MITM Proxy Telemetry System of Record (`X-Holon-*`)**:
   - Streaming performance metrics (TTFT, Prefill TPS, Tail Prefill TPS, Decode Time, Output TPS, Total Time, Prompt
     Cache Hit Rate) MUST be computed centrally inside `sandbox_executor.token_reduction.mitm_addon`.
   - Injects standardised `X-Holon-*` HTTP response headers to ensure 100% provider-agnostic and agent-agnostic
     telemetry across all containerised AI agents (`antigravity`, `claude`, `codex`, `pi`).

10. **Zero Synthetic / Mock Data Invariant for Token Reduction & Efficacy Measurements**:
    - Absolutely NO synthetic data, artificial dummy string loops (e.g., repeated dummy functions or lines in memory),
      mock stream generators, or randomised simulation loops (`generate_synthetic_iteration()`) may ever be used to
      measure or benchmark the efficacy of token reduction methods or LLM performance.
    - All token reduction benchmarks, efficacy evaluations, and scorecards must derive exclusively from authentic
      real-world data streams: (1) live containerised task executions (`holon execute`), (2) authentic wire transaction
      logs (`transactions.jsonl` containing genuine agent/tool payloads), or (3) authentic production payload JSON
      files.
    - Token accounting must be extracted directly from upstream provider response headers and usage metadata
      (`usage.input_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`,
      `usage.output_tokens`, `usage.completion_tokens_details.reasoning_tokens`) or exact BPE tokenisers, never crude
      character heuristics (`len // 4`).
    - **Mandatory Tool Calling & Artifact Production**: Benchmarks must not be restricted to conversational text-only
      loops (prompt $\to$ completion). Workloads must execute authentic multi-turn tool calling (`write_to_file`,
      `view_file`, `replace_file_content`, `run_command`, `generate_image`, `grep_search`, `find_by_name`), produce
      tangible structured deliverables (markdown artifacts with Mermaid diagrams, working code files, UI assets, and
      automated test pass logs), and exercise agent domain skills (e.g., full-stack web development or systems
      architecture ideation).

11. **Human-Only Pull Request Merging Invariant**:
    - Agents MUST NEVER merge a Pull Request, enable auto-merge, or add a PR to the merge queue.
    - Commands such as `gh pr merge` (with `--squash`, `--rebase`, `--merge`, `--auto`, etc.), `gh api` calls to merge
      endpoints, or toggling `allow_auto_merge` via `gh repo edit` are strictly prohibited.
    - Merging is strictly reserved for the human maintainer. Once all review iterations pass with consensus approval,
      the agent must stop and hand off to the human.
    - **Autonomous PR Creation in the Holon Flow**: While PR merging is strictly human-only, Pull Request _creation_ is
      autonomous when executing the Holon flow: after Stage 3 (Execute) pushes the execution branch, the agent
      autonomously raises the PR (`gh pr create`) to enable Stage 4 (PR review loop) to run unattended.

12. **Root-Only `uv` Execution & Subpackage Navigation Invariant**:
    - **NEVER** navigate (`cd`) or set `Cwd` into subpackages like `apps/sandbox-executor/` or any nested package
      directory.
    - All `uv` commands (`uv run pytest`, `uv run ruff`, `uv lock`, etc.) MUST always be executed strictly from the
      repository/workspace root.
    - **Rationale**: The root `pyproject.toml` pins `requires-python = "==3.13.*"`. Navigating into subpackage
      directories like `apps/sandbox-executor` detaches `uv` from the workspace root configuration, causing `uv` to
      invoke the ambient system Python (e.g., Python 3.14). In Python 3.14, vectorcall optimisations cause recursive
      mocking (`unittest.mock.patch.object` on `os.path` functions) to hang indefinitely at 100% CPU. Running from the
      repository root guarantees strict Python 3.13 pinning, zero test deadlocks, and clean execution.

13. **Nested Worktree Prettier Scoping Invariant**:
    - **NEVER** run global un-scoped formatting commands (e.g., `npx prettier --write "**/*.md"`) from within a nested
      target repository worktree (`apps/holon-coherence/<branch>/` or `apps/holon-agentic-coder/<branch>/`).
    - **Rationale**: Because target worktrees reside inside the harness checkout, Prettier searches parent directories
      and resolves the harness's `.prettierrc.json` (`printWidth: 100`, `proseWrap: always`). Target codebases often do
      not share this configuration, so un-scoped formatting reflows unrelated documentation and breaks CI hygiene
      checks.
    - Inside nested worktrees, agents MUST format **only the changed files** (`npx prettier --write <changed_files>`),
      use the target repository's own configuration (or `--no-config` if none exists), and verify `git diff --stat`
      before committing to ensure zero collateral files were modified.

14. **Pre-Commit Credential Leakage & Scratch File Detection Invariant (Bean 0110)**:
    - Before committing staged changes in any repository, run `uv run python .agents/scripts/pre_commit_check.py` (or
      `scripts/pre_commit_check.py` in target codebases) to ensure no API keys (`AIza...`, `ghp_...`, `github_pat_...`,
      `sk-...`, `sk-ant-...`) or disallowed ephemeral scratch paths (`tmp/*`, `*.tmp`, `*.log`, `.index/*`) are staged.

15. **Australian English (`en-AU`) Orthography Invariant (Bean 0105)**:
    - All documentation, markdown guides, skill instructions, bean specifications, and user-facing strings must use
      Australian English (`en-AU`) spelling (`standardise`, `optimise`, `synchronise`, `prioritise`, `behaviour`,
      `colour`, `catalogue`), while keeping programmatic code symbols and external API contracts unchanged.

16. **Strict Test Execution & Tooling Prohibition Invariant (NEVER `unittest`, NEVER `python3 -m unittest`, NEVER
    `PYTHONPATH`)**:
    - **NEVER** execute tests via `unittest`, `python3 -m unittest`, `python -m unittest`, or bare `pytest`.
    - **NEVER** run commands with `PYTHONPATH` overrides (e.g. `PYTHONPATH=src ...`, `export PYTHONPATH=...`).
    - All test execution across all target repositories and the harness MUST strictly use `uv run pytest` executed from
      the repository/workspace root.
    - **Rationale**: `uv` automatically manages dependencies, environment isolation, and editable package layout via
      `pyproject.toml`. Prepending `PYTHONPATH` bypasses package definitions, masks broken entry points, causes subtle
      module resolution bugs, and violates hermetic testing. Running `unittest` directly ignores `pytest` configuration,
      plugins, markers, and skips, and risks deadlocks under modern Python runtimes.

17. **Target Repository Isolation & Zero Harness Path Leaks Invariant**:
    - Target repositories (`holon-agentic-coder` and `holon-coherence`) are independent systems and MUST remain
      completely decoupled from the harness metadata repository (`holon-agentic-coder-ref-metadata`).
    - **NEVER** introduce, reference, or hardcode harness-specific paths (`.beans/`, `todo/`, `.agents/`) in any target
      repository source code, path prefix lists (e.g., `METADATA_PATH_PREFIXES`), regex patterns (e.g.,
      `SPELLING_EXEMPT_PATTERNS`), ignore lists, or test suites.
    - Inside target repositories, metadata paths are strictly limited to target-native artifacts (`holon-knowledge/`,
      `plans/`, `.holon/`). Harness concepts must never leak into target codebases under any circumstances.

18. **Canonical 3-Ledger Architecture Invariant (`holon-knowledge/ledger/`)**:
    - The Holon knowledge and provenance system operates strictly on three canonical append-only ledgers under
      `holon-knowledge/ledger/`:
      1. `intents.jsonl`: Intent records (`I-...`).
      2. `plans.jsonl`: Plan records (`P-...`).
      3. `executions.jsonl`: Unified execution ledger containing both discrete micro-actions (`entry_type: "action"`,
         `ACT-...`) and lifecycle summaries (`entry_type: "summary"`, `E-...`, `REV-...`).
    - **NEVER create auxiliary ledgers**: Under no circumstances should `actions.jsonl`, `reviews.jsonl`, or any other
      secondary JSONL ledger be introduced.
    - All action-level telemetry (test suite runs, review loop iterations, findings, GitHub dual-posts, repair steps,
      late calibration reconciliations) MUST be written exclusively to `executions.jsonl` under `LedgerLock` using
      `append_action_record()` or `append_action_event(ledger_path=executions_file)`.
    - Creating auxiliary ledgers fragments provenance, breaks downstream ledger queries, and causes split-brain state.
