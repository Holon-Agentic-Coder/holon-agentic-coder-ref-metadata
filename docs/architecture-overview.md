# Holon Ecosystem Architecture & Operational Reference

This document provides the comprehensive architectural reference, git worktree topology, and multi-agent operational
specifications for the **Holon Agentic Coder Reference Metadata** control plane.

---

## 1. Control Plane Purpose & Bootstrapping Role

`holon-agentic-coder-ref-metadata` serves as the central control plane, metadata store, and multi-agent coordination
harness for the Holon ecosystem:

- **Agent Instructions & Governance (`.agents/`)**: Canonical rules, coding standards, toolbelt invariants, and workflow
  playbooks.
- **Task Tracking (`.beans/`)**: Sequential 4-digit zero-padded task tracking database (`0001`–`0121+`) with automated
  triage and prioritisation (`prioritise-beans`).
- **Multi-Agent Skills (`.agents/skills/`)**: Reusable autonomous capabilities including the 3-agent ensemble
  `pr-reviewer`, `pr-review-resolver`, `pr-review-loop`, `clean-workspace`, `clean-branches`, `install-holon`,
  `install-coherence`, `prioritise-beans`, and `answer`.

---

## 2. The 5-Stage Holon Flow Lifecycle

Every change to a target codebase (`holon-agentic-coder` or `holon-coherence`) MUST traverse all five stages of the
Holon flow:

| Stage | Command                                | Provenance Artifact                                                                |
| :---- | :------------------------------------- | :--------------------------------------------------------------------------------- |
| **1** | `holon intent <intent.json>`           | `I-{timestamp}-{slug}/_` + `holon-knowledge/ledger/intents.jsonl`                  |
| **2** | `holon plan <intent_branch>`           | `I-.../P-{ts}-{agent}-{model}/_` + `plans/P-*.md` + `plans.jsonl`                  |
| **3** | `holon execute <plan_branch>`          | `I-.../P-.../E-{ts}-{agent}-{model}/_` + `holon-knowledge/ledger/executions.jsonl` |
| **4** | `holon review-loop` / `pr-review-loop` | Autonomous PR creation + 3-agent ensemble review + iterative resolver              |
| **5** | `holon calibrate <execution_branch>`   | `/calibrated` branch + `plans/P-*_calibration.md` merged into PR head              |

- **Dynamic Repository Resolution**: Invoking `holon` inside either `apps/holon-agentic-coder/<worktree>` or
  `apps/holon-coherence/<worktree>` dynamically resolves `remote.origin.url` via `resolve_target_repo_url()`.
- **Proactive Conflict Detection (Bean 0121)**: Each stage boundary checks for upstream divergence against `origin/main`
  and reconciles append-only JSONL ledgers deterministically.
- **Human-Only Merge Boundary (Bean 0034)**: Stage 5 calibration runs _before_ merging. Final PR merging is reserved
  exclusively for the human maintainer.

---

## 3. Target Repositories Setup (Bare Git & Worktrees)

Target repositories are cloned as bare Git databases under `apps/<project>/.git` with isolated per-agent worktrees:

### 3.1 `holon-agentic-coder` (Fractal Intent Evolution Engine)

```bash
git clone --bare git@github.com:Holon-Agentic-Coder/holon-agentic-coder.git apps/holon-agentic-coder/.git
cd apps/holon-agentic-coder/.git
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git fetch origin
git worktree add ../main main
```

### 3.2 `holon-coherence` (Optimisation Proxy Gateway & Wire Telemetry)

```bash
git clone --bare git@github.com:Holon-Agentic-Coder/holon-coherence.git apps/holon-coherence/.git
cd apps/holon-coherence/.git
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git fetch origin
git worktree add ../main main
```

### 3.3 Per-Agent Worktree Naming Conventions

- **Flow PR Worktrees**: `apps/<project>/pr<N>-<slug>` (e.g. `apps/holon-agentic-coder/pr82-flow-review-enhancements`).
- **Harness / Non-Flow Worktrees**: `apps/<project>/<type>-<bean-id>-<slug>`.
- **Temporary Verification Worktrees**: `<purpose>-<subject>-<qualifier>`, unmounted immediately upon completion.
- **Strict `main` Protection**: `apps/<project>/main` is the user's playground and is strictly read-only for agents.

---

## 4. Directory Layout Reference

```text
├── README.md                        # At-a-glance landing page & quick start
├── AGENTS.md                        # Canonical agent entrypoint & operating rules
├── LICENSE                          # Apache License 2.0
├── pyproject.toml                   # Python 3.12+ test (pytest) and lint (ruff) config
├── docs/                            # Deep architectural & audit documentation
│   ├── architecture-overview.md     # Full technical & worktree reference (this file)
│   └── ecosystem-audit-report.md    # Multi-dimensional architecture, security & DevEx audit
├── .agents/                         # Agent instructions, rules, scripts, and skills
│   ├── instructions.md              # Core agent mindset & Australian English (en-AU) standard
│   ├── rules.md                     # Coding standards, toolbelt rules, and invariants
│   ├── workflows.md                 # Task lifecycle, git conventions, and PR workflows
│   ├── coordination.md              # Subagent delegation & peer coordination protocols
│   ├── submodules.md                # Git submodules management guide
│   ├── scripts/                     # Validation & pre-commit security utilities
│   │   ├── pre_commit_check.py      # Credential leakage & scratch file detector (Bean 0110)
│   │   └── validate-links.js        # Markdown relative link validator
│   └── skills/                      # Specialized agent skills
├── .beans/                          # Sequential task database & bean-triage-prioritisation.md
├── tests/                           # Automated pytest suite for harness scripts
├── apps/                            # Git-ignored target repository bare clones & worktrees
└── todo/                            # Git-ignored local scratchpad
```
