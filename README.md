# Holon Agentic Coder — Reference Metadata & Control Plane

[![Test - Hygiene](https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref-metadata/actions/workflows/test-hygiene.yml/badge.svg)](https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref-metadata/actions/workflows/test-hygiene.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB.svg)](pyproject.toml)
[![Code Style: Prettier & Ruff](https://img.shields.io/badge/style-Prettier_%26_Ruff-f7b93e.svg)](.prettierrc.json)

## ⚡ At a Glance

`holon-agentic-coder-ref-metadata` is the central control plane, task ledger, and multi-agent orchestration harness for
the **Holon Agentic Coder** ecosystem. It provides autonomous AI agents with canonical operating rules, reusable skills,
and sequential task tracking (`.beans/`) to drive development across
[`holon-agentic-coder`](https://github.com/Holon-Agentic-Coder/holon-agentic-coder) and
[`holon-coherence`](https://github.com/Holon-Agentic-Coder/holon-coherence) via the 5-stage Holon flow.

> [!IMPORTANT] **Agent Entrypoint**: Before performing any action, run `beans prime` (if installed) and read
> [**AGENTS.md**](AGENTS.md) in its entirety. All changes to `holon-agentic-coder` and `holon-coherence` MUST be
> produced through the 5-stage Holon flow (`intent -> plan -> execute -> pr-review-loop -> calibrate`).

---

## 🚀 Key Capabilities & Improvements

| Capability                         | Description                                                                                                           | Reference                                                                          |
| :--------------------------------- | :-------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| **5-Stage Holon Flow Governance**  | Enforces end-to-end provenance (`I-.../P-.../E-.../calibrated`) and proactive conflict resolution across target repos | [AGENTS.md](AGENTS.md#-sole-change-path-the-holon-flow)                            |
| **3-Agent Ensemble Review Loop**   | Autonomous multi-agent PR review (`pr-reviewer`), validation/fixing (`pr-review-resolver`), and iterative convergence | [.agents/skills/pr_review_loop/SKILL.md](.agents/skills/pr_review_loop/SKILL.md)   |
| **Sequential Bean Task Ledger**    | File-based task tracking in `.beans/` with automated triage and priority matrix generation (`prioritise-beans`)       | [.beans/bean-triage-prioritisation.md](.beans/bean-triage-prioritisation.md)       |
| **Workspace & Branch Hygiene**     | Automated cleanup of merged worktrees, provenance trees, orphaned folders, and 30-day `.subagent/` archives           | [.agents/skills/clean_workspace/SKILL.md](.agents/skills/clean_workspace/SKILL.md) |
| **Pre-Commit Security Guardrails** | Blocks leaked credentials (`AIza...`, `ghp_...`, `sk-...`) and ephemeral scratch files (`tmp/*`, `.index/*`)          | [.agents/scripts/pre_commit_check.py](.agents/scripts/pre_commit_check.py)         |
| **Buildx Bake & CLI Installers**   | One-command container builds and global `uv tool install` for `holon` and `holon-coherence`                           | [.agents/skills/install_holon/SKILL.md](.agents/skills/install_holon/SKILL.md)     |

---

## 🛠️ Quick Getting Started

### 1. Initialise Target Repository Bare Clones & Worktrees {#-target-repositories-setup-git-worktree}

```bash
# 1. Clone holon-agentic-coder bare repository and main worktree
git clone --bare git@github.com:Holon-Agentic-Coder/holon-agentic-coder.git apps/holon-agentic-coder/.git
git --git-dir=apps/holon-agentic-coder/.git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git --git-dir=apps/holon-agentic-coder/.git fetch origin
git --git-dir=apps/holon-agentic-coder/.git worktree add apps/holon-agentic-coder/main main

# 2. Clone holon-coherence bare repository and main worktree
git clone --bare git@github.com:Holon-Agentic-Coder/holon-coherence.git apps/holon-coherence/.git
git --git-dir=apps/holon-coherence/.git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git --git-dir=apps/holon-coherence/.git fetch origin
git --git-dir=apps/holon-coherence/.git worktree add apps/holon-coherence/main main
```

### 2. Run Harness Verification & Tests

```bash
uv sync --group dev
uv run ruff check .agents/ tests/
uv run pytest tests/ -q
npx prettier --check "**/*.md"
node .agents/scripts/validate-links.js
```

---

## 🧭 Documentation & Navigation Matrix

- [**AGENTS.md**](AGENTS.md) — Canonical agent landing page, incoming checklist, and human-only PR merge boundary.
- [**docs/architecture-overview.md**](docs/architecture-overview.md) — Detailed architectural reference, git worktree
  setup mechanics, and directory layout.
- [**docs/ecosystem-audit-report.md**](docs/ecosystem-audit-report.md) — Multi-dimensional audit report covering code
  quality, security hermeticity, and DevEx.
- [**.agents/instructions.md**](.agents/instructions.md) — Core mindset, operational guidelines, and Australian English
  (`en-AU`) orthography standard.
- [**.agents/rules.md**](.agents/rules.md) — Coding standards, toolbelt constraints, and permanent engineering
  invariants.
- [**.agents/workflows.md**](.agents/workflows.md) — Bean lifecycle, git branch conventions, and PR review procedures.
- [**.beans/bean-triage-prioritisation.md**](.beans/bean-triage-prioritisation.md) — Live ecosystem bean triage and
  prioritisation matrix.

---

## 📄 Licence

Licensed under the [Apache License 2.0](LICENSE).
