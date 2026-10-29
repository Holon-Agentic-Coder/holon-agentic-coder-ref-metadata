# General Agent Instructions

As an autonomous AI agent in the Holon Agentic Coder ecosystem, you are responsible for maintaining high code quality,
system safety, and clean documentation. Follow these core guidelines in every session.

---

## 🧠 Core Agent Mindset

1. **Be Rigorous**: Do not make assumptions about the codebase structure or behaviour. Always read the code and test
   suites before making changes.
2. **Be Minimalist**: Write clean, readable, and well-targeted code. Avoid introducing unnecessary dependencies or
   over-engineering solutions.
3. **Be Communicative**: Inform the user (or parent agent) of your plan before executing complex steps. Use artifacts to
   outline detailed multi-step plans.
4. **Preserve Context**: Maintain original documentation, comments, and structure unless explicitly tasked with changing
   them. Do not delete comments or rename files without justification.
5. **Avoid Absolute Paths**: Never use absolute file paths in code references, comments, tasks, or documentation. Always
   use paths relative to the project root (e.g. `.agents/instructions.md`) to ensure portability across developer
   workspaces.

---

## 🛠 Operational Guidelines

### 1. Research and Discovery

- Before modifying a file, read its entire contents (or at least the surrounding context up to 800 lines) using the file
  viewer tool.
- Use grep searches to locate all occurrences of a variable, class, or function you plan to change to avoid breaking
  downstream references.

### 2. Edits and Modifications

- Prefer making precise, targeted edits using specific search-and-replace tools rather than rewriting entire files.
- Ensure that the lines you are replacing are unique and match exactly, including leading whitespace and indentation.
- Always lint and/or compile files immediately after editing to catch syntax or logical errors early.

### 3. Verification and Safety

- Never assume your edits work. Always execute tests or verification scripts to prove correctness.
- If no test suite exists, write unit tests directly within the codebase to verify your changes, rather than relying on
  untracked external scratch files.
- Check git status and diff output to ensure only the intended changes have been made.

### 4. Workspace Structure (`apps/`)

- Target application codebases reside under the `apps/` directory (`apps/holon-agentic-coder` and
  `apps/holon-coherence`).
- **All `holon-agentic-coder` and `holon-coherence` code modifications must be produced by the 5-stage Holon flow**
  (intent -> plan -> execute -> PR review loop -> calibration) as sandbox-authored commits on `I-.../P-.../E-...`
  branches. Running `holon` inside either target repository worktree dynamically resolves `remote.origin.url` via
  `resolve_target_repo_url()`. Manual stage-by-stage commands are as compliant as `holon flow`; skipping any stage is
  not. See the Sole Change Path rule in `AGENTS.md` and invariant 8 in `.agents/rules.md`.
- Repository worktrees (e.g. `apps/holon-agentic-coder/{branch}` or `apps/holon-coherence/{branch}`) are for building
  images, reading code, running verification, and operating the harness -- never for hand-authoring target codebase
  source changes outside the flow.
- The repository root is strictly for control plane coordination, task tracking (`.beans/`), and agent guidance; those
  harness files are edited directly, since the flow does not target this metadata repository.

### 5. Subagent Delegation (AGY & Generic Coding Agents)

- Subagent delegation in this ecosystem is primarily targeted towards the **Antigravity (AGY)** runtime:
  - Use `invoke_subagent` with `TypeName: "self"` so child agents inherit full tools (view, edit, bash execution) and
    environment settings. Use `TypeName: "research"` for read-only research.
  - Set `Model: "inherit"` to match the parent agent's configuration.
  - **Automatic Model Tier Fallback on Credit/Quota Exhaustion**: Applies to both **Claude** and **Antigravity**. When a
    higher-level model runs out of credit, session quota, or rate-limit allowance, automatically fall back to the next
    lower model tier that has credit and continue the flow or review loop from the current stage/branch without
    restarting completed stages:
    - **Claude (`claude-agent` / Claude Code)**: `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6` $\rightarrow$
      `claude-haiku-4-5`.
    - **Antigravity (`antigravity-agent` in `holon` CLI)**: `gemini-3.8-pro-high` $\rightarrow$
      `gemini-3.8-flash-medium` $\rightarrow$ `gemini-3.8-flash`.
    - **Antigravity (`invoke_subagent` in AGY runtime)**: `Model: "inherit"` / `"pro"` $\rightarrow$ `"flash"`
      $\rightarrow$ `"flash_lite"`.
    - **Cross-Runner Continuation**: If an entire runner's session quota is exhausted across all its model tiers (e.g.
      Claude OAuth session limit), switch `--agent` to the alternate runner (`antigravity-agent` or `claude-agent`) and
      continue the flow from the current stage (`holon plan <intent_branch>`, `holon execute <plan_branch>`,
      `holon review <execution_branch>`, or `holon calibrate <execution_branch>`).
  - Never poll or sleep in a loop; AGY wakes the parent agent automatically when child tasks finish.
- Generic coding agents (such as Claude Code, Codex, Pi, OpenCodeInterpreter) can execute child tasks using their native
  subagent or child process delegation mechanisms following the same prompt contracts.

### 6. Token Conservation & Concise Communication (Harness & Subagents)

- **Strict Brevity**: Minimise both prompt and completion token consumption across the main harness and all subagents.
- **Concise Reporting**: Do not produce verbose discursive explanations or repeat full file diffs. Keep responses dense,
  factual, and strictly actionable.
- **Targeted Subagent Prompts & Reports**: Subagent prompts and deliverables must be focused strictly on their immediate
  evaluation or task contract. Reviewers must return structured findings tables and summary blocks rather than narrative
  essays.
- **No Premature External Comments**: PR consensus review comments must only be published to GitHub when the ensemble
  review is fully complete and all findings are definitively classified or resolved. Intermediate iterations stay local
  to `.subagent/`.
- **Subagent Cleanup**: Merged, stale, or superseded patch, diff, and review files in `.subagent/` must be pruned or
  archived immediately once their respective iteration or PR lifecycle completes.

### 7. Australian English (`en-AU`) Orthography Standard (Bean 0105)

- **House Style**: All documentation, agent instructions, skill guides, bean descriptions, commit messages, PR bodies,
  and user-facing copy across the Holon ecosystem MUST use **Australian English (`en-AU`)** spelling (e.g.
  `standardise`, `optimise`, `synchronise`, `prioritise`, `categorise`, `behaviour`, `colour`, `catalogue`, `licence` as
  noun / `license` as verb).
- **Code & API Preservation**: Programmatic identifiers, standard library symbols, configuration keys, CLI flags, and
  external API contracts (e.g. `initialize`, `Authorization`, `color` in CSS/HTML) must remain unchanged to preserve
  compatibility.

### 8. Target Repository Isolation & Zero Harness Leaks

- **Strict Boundary**: Target codebases (`apps/holon-agentic-coder`, `apps/holon-coherence`) are independent systems and
  must remain strictly agnostic to the harness metadata repository (`holon-agentic-coder-ref-metadata`).
- **Zero Leakage**: Never reference, import, or hardcode harness directories (`.beans/`, `todo/`, `.agents/`) in target
  repository source code, path prefix lists, ignore patterns, calibration metrics, pre-commit checks, or test suites.

### 9. Strict Test Execution & Tooling Standards

- **Exclusively `uv run pytest`**: All tests must be run using `uv run pytest` from the repository root.
- **NEVER `unittest`**: Never invoke `unittest`, `python3 -m unittest`, or bare `pytest`.
- **NEVER `PYTHONPATH`**: Never prefix or export `PYTHONPATH`. `uv` cleanly manages editable package resolution; manual
  overrides mask packaging defects and break hermetic testing.

### 10. Canonical 3-Ledger Architecture (`holon-knowledge/ledger/`)

- **Strict 3-Ledger Triad**: All Holon provenance and lifecycle events are strictly confined to three canonical ledgers:
  `intents.jsonl`, `plans.jsonl`, and `executions.jsonl`.
- **NEVER Create Auxiliary Ledgers**: Never create `actions.jsonl`, `reviews.jsonl`, or any secondary ledger file.
- **Interleaved Actions**: All discrete action records (`entry_type: "action"`) and lifecycle summaries
  (`entry_type: "summary"`) must be appended exclusively to `executions.jsonl` under advisory file locking
  (`LedgerLock`).
