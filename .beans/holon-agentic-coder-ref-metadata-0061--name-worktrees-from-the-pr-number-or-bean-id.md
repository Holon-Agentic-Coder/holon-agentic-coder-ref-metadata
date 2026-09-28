---
# holon-agentic-coder-ref-metadata-0061
title: "Name worktrees from the PR number or bean id"
status: completed
type: task
priority: normal
tags:
  - worktree
  - git
  - conventions
  - cleanup
created_at: 2026-09-28T11:37:47Z
updated_at: 2026-09-28T11:49:12Z
---

Worktree directory names in this workspace are unattributable. `git worktree list` exposes only path, commit and
refname, so a cleanup pass can only judge a directory by what its name says. The live workspace demonstrated the cost:
the PR #60 / PR #61 checkouts on this bean's date were `resolve-0019-a`, `resolve-0019-b`, `calib-0019-a`,
`calib-0019-b`, `verify-0019-a` and `verify-0019-b` -- six directories whose only differentiator was a letter suffix,
none of which names the PR or the purpose it belongs to.

Operator instruction, as clarified while this bean was being written:

1. If the worktree is checked out **from a Holon flow branch** (`I-xxx/P-xxx/E-xxx`), there is a Pull Request, so the
   name MUST carry the **PR number and a slug**.
2. If there is **no Holon flow branch**, the name MUST carry the **bean number**.
3. A worktree created **for temporary use** MUST be named **as descriptively as possible**.

## Naming rule adopted

| Situation                                       | Directory                                                                                  | Branch                                                           |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Checkout of a flow branch `I-.../P-.../E-.../_` | `apps/<project>/pr<N>-<slug>` e.g. `pr61-agent-output-capture`                             | the flow ref, verbatim -- never renamed or re-cut                |
| Hand-authored harness / `holon-coherence` work  | `apps/<project>/<type>-<bean-id>-<slug>`                                                   | `<type>/<bean-id>-<slug>` e.g. `fix/0027-host-local-llm-routing` |
| Temporary checkout                              | `apps/<project>/<purpose>-<subject>-<qualifier>` e.g. `verify-pr61-agent-output-redaction` | own branch, same name                                            |

Opaque names are prohibited: `tmp`, `wip`, `scratch`, `test1`, `worktree2`, and letter-suffixed families such as
`resolve-a` / `calib-b` / `verify-0019-a`. A temporary worktree is deleted when its stated purpose completes. Work that
has neither a PR nor a bean is logged as a bean first, then gets a worktree.

## Scope

Instruction documents only -- control-plane files, directly editable under the `AGENTS.md` harness exception:

- `AGENTS.md` -- checklist item 5 (Per-Agent Worktrees) naming rules, plus where a metadata-repo worktree belongs
  (`apps/holon-agentic-coder-ref-metadata/{branch-dir}`, under the git-ignored `apps/`).
- `.agents/workflows.md` -- Git guidelines rule 1 and the branch naming convention bullet.
- `README.md` -- worktree setup steps for both target repositories.

## Resolution

- Added the three-way naming rule above to `AGENTS.md` item 5 and `.agents/workflows.md` rule 1, and the short form to
  both `README.md` setup steps.
- Recorded the flow-branch exception explicitly: a `I-.../P-.../E-.../...` head keeps its exact ref name because it is
  the audited provenance record, so the `pr<N>-<slug>` marker lives on the **directory**.
- Worktree used for this change follows the rule it introduces and had to invent the metadata-repo location:
  `apps/holon-agentic-coder-ref-metadata/docs-0061-worktree-naming-conventions` (branch
  `docs/0061-worktree-naming-conventions`, off `origin/main` `3ebbeb6`), leaving the user's active checkout on
  `docs/bean-0019-closeout-and-followups` untouched.
- Markdown formatted with `npx prettier --write "**/*.md"`.

## Follow-ups

- Existing `apps/holon-agentic-coder/{resolve,calib,verify}-0019-*` directories predate this rule. Renaming means
  `git worktree move`, which is only worth doing on the next teardown-and-recreate, and any cleanup is gated on the
  human confirming the PR #61 merge.
