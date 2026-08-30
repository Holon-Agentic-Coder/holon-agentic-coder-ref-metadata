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
     directory. Never invoke `python3`, `pytest`, or `.venv` binaries directly.
     - **Unit Test Execution**: Run unit tests using `uv run pytest -m "not integration_test"` from the repository root.
     - **Integration Test Execution**: When running integration tests, first build required container images using
       `./apps/sandbox-executor/build_all_images.sh --output-log`, then run `uv run pytest -m "integration_test"`.
     - **Linting & Lockfile Check**: Validate linting, formatting, and lockfile integrity using: `uv lock --check`,
       `uv run ruff check .`, and `uv run ruff format --check .`.
   - **Single Project `.venv`**: Always execute `uv` commands from the repository/project root so that virtual
     environments are maintained solely in the root `.venv`. Never create or initialize nested `.venv` directories in
     subfolders (e.g., `apps/sandbox-executor/.venv`).
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
5. **Universal Agent Credentials (`HOLON_AGENT_KEY`)**:
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

4. **No `PYTHONPATH=...` Command Style & `uv` Enforcement**:
   - Never use `PYTHONPATH=... python3` for testing or running scripts. Always execute tests and commands using `uv`
     (e.g., `uv run pytest`).

5. **Strict Repository Separation (Implementation vs Metadata)**:
   - `holon-agentic-coder-ref-metadata` is the control plane harness and metadata store
     (`git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref-metadata.git`).
   - `holon-agentic-coder-ref` is the target implementation codebase
     (`git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git`), located inside the `holon-agentic-coder-ref/`
     directory.
   - NEVER mix up their git remotes, working directories, commit histories, or task contexts. Commands targeting
     `holon-agentic-coder-ref` must be executed strictly inside `holon-agentic-coder-ref/` (or its git worktrees), and
     the `origin` remote of `holon-agentic-coder-ref-metadata` must NEVER be altered to point to
     `holon-agentic-coder-ref.git`.
