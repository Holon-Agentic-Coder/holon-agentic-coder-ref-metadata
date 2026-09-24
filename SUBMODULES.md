# Git Submodules: Ecosystem Guide

This document outlines how Git submodules are managed across the **Holon Agentic Coder** ecosystem, focusing on the
**`holon-coherence`** submodule embedded within **`holon-agentic-coder`**.

> [!NOTE] When operating within this control plane workspace (`holon-agentic-coder-ref-metadata`), the parent repository
> **`holon-agentic-coder`** is located at **`apps/holon-agentic-coder/main`** (or a dedicated worktree). Always navigate
> to that worktree root before executing submodule commands. For internal agent operating protocols and execution
> workflows, see [.agents/submodules.md](.agents/submodules.md).

---

## 1. Overview & Mechanics

Git submodules allow one repository to nest another repository at a specific path while keeping their commit histories
completely separate.

### Key Components

- **`.gitmodules` (Text Configuration)**: Located at the root of the parent repository. Maps the submodule path to the
  remote repository URL and default tracking branch.

  ```ini
  [submodule "holon-coherence"]
  	path = holon-coherence
  	url = https://github.com/Holon-Agentic-Coder/holon-coherence.git
  	branch = main
  ```

  > [!IMPORTANT] Always use public `https://` URLs in `.gitmodules`. Do not use SSH URLs (`git@github.com:...`), as
  > CI/CD runners, Docker builds, and automated execution sandboxes clone repositories without user SSH keys.

- **Git Tree Entry / Gitlink (`160000`)**: Git stores the exact submodule commit pointer as a binary tree entry with
  mode `160000`:
  ```text
  160000 commit 87dc438254e5c229d3b46fb8a4afe03febf4a7e8 holon-coherence
  ```
  Git **never** automatically advances the submodule to the remote branch tip. It remains pinned to this exact commit
  until explicitly updated and committed.

---

## 2. Common Operations

### Initializing Submodules

When checking out a worktree or fresh clone (from `apps/holon-agentic-coder/main` or target worktree):

```bash
git submodule update --init --recursive
```

### Checking Status

```bash
git submodule status
git ls-tree HEAD holon-coherence
```

### Updating to the Latest Main Commit

```bash
git submodule update --remote --merge holon-coherence
git add holon-coherence
git commit -m "chore(submodule): update holon-coherence to $(git -C holon-coherence rev-parse --short HEAD)"
```

### Pinning to a Specific Commit or Tag

```bash
cd holon-coherence
git fetch origin
git checkout <commit-sha-or-tag>
cd ..
git add holon-coherence
git commit -m "chore(submodule): pin holon-coherence to <commit-sha>"
```

### CI / GitHub Actions Setup

```yaml
- name: Checkout repository and submodules
  uses: actions/checkout@v4
  with:
    submodules: true
```
