# Holon Agentic Coder Reference Metadata

> [!NOTE] **Bootstrapping Harness Intent** This repository is a temporary control plane and metadata store. It will only
> be used until the bootstrap process for
> [holon-agentic-coder-ref](https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref) is fully completed. Until
> that repository is fully bootstrapped, it does not possess enough autonomous power to develop or maintain itself. This
> repository serves as the external harness to bridge that gap.

**IMPORTANT**: before you do anything else, run the `beans prime` command and heed its output.

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

## 📥 Reference Repository Setup (Git Worktree)

To work with the primary codebase repository
([holon-agentic-coder-ref](https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref)) alongside this metadata
repository, you must clone it as a Git bare repository and check out branches as Git worktrees. This allows running
multiple tasks on different branches simultaneously under a clean directory structure.

Follow these steps to set it up:

1. **Clone the repository as bare** into the `holon-agentic-coder-ref` directory:
   ```bash
   git clone --bare git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git holon-agentic-coder-ref
   ```
2. **Navigate into the directory**:
   ```bash
   cd holon-agentic-coder-ref
   ```
3. **Set up worktrees for your branches**:
   - **For the `develop` branch** (checked out to `holon-agentic-coder-ref/develop`): This is the primary active
     development branch where all codebase features, bug fixes, and development take place.
     ```bash
     git worktree add develop develop
     ```
   - **For the `main` branch** (checked out to `holon-agentic-coder-ref/main`): This branch is from the upstream
     repository and only contains documentation and specifications.
     ```bash
     git worktree add main main
     ```
   - **For a specific branch `{branch_name}`** (checked out to `holon-agentic-coder-ref/{branch_name}`):
     ```bash
     git worktree add {branch_name} {branch_name}
     ```

## 📂 Directory Structure

```text
├── README.md                # General repository information (this file)
├── AGENTS.md                # Entry point & landing page for agents
├── .agents/                 # Core agent configurations and instructions
│   ├── instructions.md      # General operational instructions for coding agents
│   ├── rules.md             # Code standards, formatting, and behavioral constraints
│   ├── workflows.md         # Step-by-step developer and release workflows
│   └── coordination.md      # Protocols for multi-agent communication and subagent management
└── .beans/                  # Text-based task and issue tracking database (managed via .beans.yml)
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
