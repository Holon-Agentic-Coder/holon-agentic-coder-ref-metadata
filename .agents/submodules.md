# Git Submodules Management Guide

> [!NOTE] This guide outlines how Git submodules are managed across the **Holon Agentic Coder** ecosystem, using the
> **`holon-coherence`** submodule in **`holon-agentic-coder`** as the primary example.
>
> In this control plane repository (`holon-agentic-coder-ref-metadata`), the parent repository **`holon-agentic-coder`**
> is maintained under **`apps/holon-agentic-coder/main`** (or a dedicated worktree branch
> `apps/holon-agentic-coder/<worktree>`). Submodule operations must be executed from within that worktree root, never
> directly from the metadata repository root.

---

## 1. Submodule Mechanics: Pinned Commits vs. Configuration

A Git submodule embeds another Git repository into a subdirectory while preserving independent version control history
and separate remotes.

Git tracks submodules through two separate mechanisms:

### A. `.gitmodules` (Repository Configuration)

Stored at the root of the parent repository (`apps/holon-agentic-coder/main/.gitmodules`). Defines the mapping of the
local directory to the remote URL and default tracking branch:

```ini
[submodule "holon-coherence"]
	path = holon-coherence
	url = https://github.com/Holon-Agentic-Coder/holon-coherence.git
	branch = main
```

> [!IMPORTANT] **Always use public `https://` URLs** rather than SSH (`git@github.com:...`) URLs. GitHub Actions
> runners, CI/CD pipelines, Docker builders, and automated sandboxes must be able to clone public submodules without
> requiring custom SSH private keys.

### B. Git Tree / Index (`160000` Gitlink)

The submodule commit pointer is **not stored in a text file**. It is stored in Git's binary tree object
(`.git/objects/`) and staging index (`.git/index`) as a special entry with file mode `160000` (gitlink):

```text
160000 commit 87dc438254e5c229d3b46fb8a4afe03febf4a7e8 holon-coherence
```

- **Strict Pinning**: Git **never** automatically pulls or advances the submodule to the remote branch tip.
- The parent repository stays pinned to that exact commit SHA until you explicitly stage and commit a new commit
  pointer.

---

## 2. Initializing & Populating Submodules

When checking out a fresh clone or creating a new Git worktree under `apps/holon-agentic-coder/`, submodule directories
are created empty. You must explicitly initialize and fetch them:

```bash
# 1. From the metadata repository harness, navigate to the parent repository worktree:
cd apps/holon-agentic-coder/main
# (or cd apps/holon-agentic-coder/<branch-worktree>)

# 2. In the parent worktree root, initialize and populate submodules:
git submodule update --init --recursive
```

To clone a repository and initialize all submodules in one command:

```bash
git clone --recurse-submodules <repo-url>
```

---

## 3. Adding a Submodule (Example: `holon-coherence`)

To embed an external repository as a submodule:

```bash
# 1. Inside the parent worktree (e.g. apps/holon-agentic-coder/main):
git submodule add -b main https://github.com/Holon-Agentic-Coder/holon-coherence.git holon-coherence

# 2. Inspect the staged files (.gitmodules and gitlink 160000):
git status
git ls-files --stage holon-coherence

# 3. Commit the new submodule:
git commit -m "feat(submodule): add holon-coherence submodule tracking main"
```

---

## 4. Updating Submodules to Newer Commits

When upstream updates occur on `holon-coherence`, you can advance the submodule pointer using either of two methods:

### Method A: Fast-forward using the configured branch (`main`)

```bash
# From the parent worktree root (apps/holon-agentic-coder/main):
git submodule update --remote --merge holon-coherence

# Stage and commit the updated commit SHA:
git add holon-coherence
git commit -m "chore(submodule): update holon-coherence to $(git -C holon-coherence rev-parse --short HEAD)"
```

### Method B: Explicitly pin to a specific commit or tag

```bash
# From the parent worktree root (apps/holon-agentic-coder/main):
cd holon-coherence
git fetch origin
git checkout <commit-sha-or-tag>
cd ..

# Stage the new 160000 gitlink:
git add holon-coherence
git commit -m "chore(submodule): pin holon-coherence to <commit-sha>"
```

---

## 5. Inspecting Submodule Status

From the parent worktree root (`apps/holon-agentic-coder/main`):

- **Status overview**:

  ```bash
  git submodule status
  ```

  Prefix symbols:
  - ` ` (space): Submodule is clean and matches the commit recorded in the parent repository.
  - `-` (minus): Submodule is uninitialized (run `git submodule update --init`).
  - `+` (plus): Checked-out commit in submodule directory differs from the pinned commit in the parent index.
  - `U` (uppercase U): Submodule has merge conflicts.

- **Inspect the exact pinned tree object**:

  ```bash
  git ls-tree HEAD holon-coherence
  # Output: 160000 commit <sha> holon-coherence
  ```

- **Inspect the staging index**:
  ```bash
  git ls-files --stage holon-coherence
  # Output: 160000 <sha> 0 holon-coherence
  ```

---

## 6. Developing Inside a Submodule

When developing changes directly inside the embedded `holon-coherence/` folder:

1. From the metadata harness root, navigate into the embedded submodule inside the parent worktree:
   ```bash
   cd apps/holon-agentic-coder/main/holon-coherence
   git checkout -b feat/<feature-name>
   ```
2. Make code edits, test, and commit inside the submodule:
   ```bash
   git add .
   git commit -m "feat: implement feature in holon-coherence"
   git push origin feat/<feature-name>
   ```
3. Return to the parent repository worktree root, stage the new commit pointer, and commit:
   ```bash
   cd ..
   git add holon-coherence
   git commit -m "chore(submodule): advance holon-coherence to feat/<feature-name>"
   ```

---

## 7. Continuous Integration (CI) Configuration

Workflows in `.github/workflows/` that test or build code depending on submodules must instruct `actions/checkout` to
fetch submodules:

```yaml
- name: Checkout repository and submodules
  uses: actions/checkout@v4
  with:
    submodules: true
```

If submodules have nested submodules of their own:

```yaml
submodules: recursive
```

---

## 8. Removing a Submodule

To cleanly remove a submodule from a repository (executed inside the parent worktree `apps/holon-agentic-coder/main`):

```bash
# 1. De-register the submodule from local .git/config:
git submodule deinit -f holon-coherence

# 2. Remove the submodule from the working tree and .gitmodules:
git rm -f holon-coherence

# 3. Clean up the internal Git object cache:
rm -rf .git/modules/holon-coherence

# 4. Commit the deletion:
git commit -m "chore(submodule): remove holon-coherence submodule"
```
