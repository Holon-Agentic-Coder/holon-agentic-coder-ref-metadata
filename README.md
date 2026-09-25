# Holon Agentic Coder Reference Metadata

> [!NOTE] **Bootstrapping Harness Intent** This repository is a temporary control plane and metadata store. It will only
> be used until the bootstrap process for
> [holon-agentic-coder](https://github.com/Holon-Agentic-Coder/holon-agentic-coder) is fully completed. Until that
> repository is fully bootstrapped, it does not possess enough autonomous power to develop or maintain itself. This
> repository serves as the external harness to bridge that gap.

**IMPORTANT**: before you do anything else, run the `beans prime` command and heed its output. This requires the
[`beans` CLI](https://github.com/hmans/beans) to be installed and on your `PATH`; it is **not** part of this repository.
If `beans` is not installed, skip the command and work directly from [AGENTS.md](AGENTS.md) plus the bean files in
[`.beans/`](.beans/), following the format rules in
[.agents/workflows.md](.agents/workflows.md#-task-lifecycle-the-bean-system).

This repository acts as the central control plane, metadata store, and coordination hub for agentic workflows operating
on the **Holon Agentic Coder** ecosystem.

It defines how autonomous AI coding agents interact, coordinate, track tasks, and execute instructions to maintain and
develop codebases within this organization.

## 📌 Repository Purpose

Autonomous agents require shared context, explicit operating guidelines, and standardized task tracking to operate
efficiently and safely. This repository provides:

1. **Agent Instructions:** Guidelines, playbooks, and constraints for coding agents (`.agents/`).
2. **Coordination Protocols:** Procedures for multi-agent interaction, subagent delegation, and handoffs
   ([AGENTS.md](AGENTS.md)).
3. **Task Tracking:** A lightweight, text-based task database using the `.beans` schema (`.beans/`) to record goals,
   statuses, and history without heavy external dependencies.

## 📥 Target Repositories Setup (Git Worktree)

To work with codebase repositories within this metadata repository, you must clone them as Git bare repositories and
check out branches as Git worktrees. This allows running multiple tasks on different branches simultaneously under a
clean directory structure.

### 1. `holon-agentic-coder` (Primary Fractal Intent Evolution Engine)

Located at `apps/holon-agentic-coder/`:

1. **Clone the repository as bare** into the hidden `.git` folder of the `apps/holon-agentic-coder` directory:
   ```bash
   git clone --bare git@github.com:Holon-Agentic-Coder/holon-agentic-coder.git apps/holon-agentic-coder/.git
   ```
2. **Navigate into the git database directory and configure fetch refspec**:
   ```bash
   cd apps/holon-agentic-coder/.git
   git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
   git fetch origin
   ```
3. **Set up worktrees for your branches**:
   - **For the `main` branch** (checked out to `apps/holon-agentic-coder/main`): This is the primary active branch
     tracking `origin/main`.
     ```bash
     git worktree add ../main main
     ```
   - **For a specific feature branch `{branch_name}`** (checked out to `apps/holon-agentic-coder/{branch_name}`): All
     development and feature changes must be branched off `origin/main`:
     ```bash
     git worktree add --no-track -b {branch_name} ../{branch_name} origin/main
     ```

### 2. `holon-coherence` (Optimization Gateway & Wire Telemetry)

Located at `apps/holon-coherence/`:

1. **Clone the repository as bare** into the hidden `.git` folder of the `apps/holon-coherence` directory:
   ```bash
   git clone --bare git@github.com:Holon-Agentic-Coder/holon-coherence.git apps/holon-coherence/.git
   ```
2. **Navigate into the git database directory and configure fetch refspec**:
   ```bash
   cd apps/holon-coherence/.git
   git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
   git fetch origin
   ```
3. **Set up worktrees for your branches**:
   - **For the `main` branch** (checked out to `apps/holon-coherence/main`): This is the baseline active branch for the
     coherence proxy gateway.
     ```bash
     git worktree add ../main main
     ```
   - **For a specific feature branch `{branch_name}`** (checked out to `apps/holon-coherence/{branch_name}`): All
     development and feature changes must be branched off `origin/main`:
     ```bash
     git worktree add --no-track -b {branch_name} ../{branch_name} origin/main
     ```

## 📂 Directory Structure

```text
├── README.md                # General repository information (this file)
├── AGENTS.md                # Entry point & landing page for agents
├── SUBMODULES.md            # Git submodules ecosystem guide
├── .agents/                 # Core agent configurations and instructions
│   ├── instructions.md      # General operational instructions for coding agents
│   ├── rules.md             # Code standards, formatting, and behavioral constraints
│   ├── workflows.md         # Step-by-step developer and release workflows
│   ├── submodules.md        # Submodule operational workflows and CI guidance
│   └── coordination.md      # Protocols for multi-agent communication and subagent management
├── .beans/                  # Text-based task and issue tracking database (managed via .beans.yml)
├── apps/                    # Target application repositories (git ignored)
│   ├── holon-agentic-coder/ # Primary engine codebase (bare git + worktree main)
│   └── holon-coherence/     # Coherence proxy & optimization gateway (bare git + worktrees main)
└── todo/                    # Local temporary scratchpad for images, docs, and notes (git ignored)
```

## 🛠 How Agents Use This Repo

When an agent is initialized in this workspace:

1. **Read the Entrypoint:** The agent must read [AGENTS.md](AGENTS.md) first to understand the workspace structure and
   its role.
2. **Consult Instructions:** Refer to [.agents/instructions.md](.agents/instructions.md) and
   [.agents/rules.md](.agents/rules.md) before writing code.
3. **Sync Tasks:** Use the `.beans/` directory to look up assigned tasks or log progress following the guidelines in
   [.agents/workflows.md](.agents/workflows.md).

## 🤝 Contributing & Maintenance

Humans and senior manager agents can edit files in `.agents/` to refine rules or add new protocols as the codebase and
requirements evolve. All changes should be committed using clean semantic commit messages on dedicated feature branches.
