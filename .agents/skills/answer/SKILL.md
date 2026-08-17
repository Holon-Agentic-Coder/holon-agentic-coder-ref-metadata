---
name: answer
description:
  Answers user questions, explains concepts, conducts codebase research, and analyzes architecture in pure read-only
  mode. Strictly prohibits any actions, code modifications, file writes, git commits, or state-altering mutations.
  Activate this skill whenever the user invokes `/answer`, asks a question, or explicitly requests an answer with no
  actions.
---

# Answer Skill (`/answer`)

The **Answer Skill** ensures the agent operates in a strict **Read-Only / Pure Advisory** mode. When this skill is
active, the agent focuses exclusively on answering queries, explaining technical concepts, clarifying system
architecture, and offering advice without executing any mutations or actions on the workspace.

---

## 🔒 Core Invariants (Strictly No Action)

When responding under the `/answer` skill, you must adhere to the following non-negotiable rules:

1. **Zero File Mutations**:
   - **DO NOT** create, edit, overwrite, delete, or rename any project files.
   - **DO NOT** use `write_to_file`, `replace_file_content`, or similar editing tools to modify codebase or workspace
     files.

2. **Zero Git or State-Altering Commands**:
   - **DO NOT** run commands that create branches, stage files (`git add`), commit (`git commit`), rebase
     (`git rebase`), reset, or push (`git push`).
   - **DO NOT** install dependencies, build packages, or run commands that create side effects or alter system state.

3. **Read-Only Research Allowed (Information Gathering Only)**:
   - You may use read-only inspection tools (`view_file`, `grep_search`, `list_dir`, `search_web`, `read_url_content`)
     **only if necessary** to look up facts, verify codebase references, or retrieve accurate context to answer the
     user's question.
   - If the existing conversation context is already sufficient to answer, answer directly without making unnecessary
     tool calls.

---

## 💡 Response Format & Best Practices

When delivering answers under this skill:

- **Clear & Direct**: Provide a direct, unambiguous answer to the user's prompt without preamble or unnecessary
  disclaimers.
- **Structured & Scannable**: Use Markdown headings, bullet points, code blocks, comparison tables, or Mermaid diagrams
  to illustrate concepts cleanly.
- **Illustrative Code Blocks**: Any code snippets must be provided within the chat response as standard markdown code
  fences for explanatory purposes only—never written to disk.
- **Decision Tradeoffs**: When answering design or architecture questions, clearly present the rationale, pros/cons, and
  recommended alternatives.
