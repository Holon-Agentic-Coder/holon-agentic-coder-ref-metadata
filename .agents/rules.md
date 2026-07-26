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
