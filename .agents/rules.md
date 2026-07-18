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
2. **File Editing**:
   - Use `replace_file_content` for a single contiguous block of edits.
   - Use `multi_replace_file_content` for editing multiple non-contiguous blocks in the same file.
   - Never overwrite an entire file with `write_to_file` if you are only making minor edits.
3. **Sandboxing and Security**:
   - Do not attempt to run processes that modify root system directories or execute outside the defined workspace
     directories.
   - If you trigger a permission error, request the minimum required permissions using `ask_permission`.
