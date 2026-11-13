---
# holon-agentic-coder-ref-metadata-0275
title: "Decomposed flows build branch names longer than GitHub's ref limit; cap and shorten them"
status: completed
type: bug
priority: high
tags:
  - flow
  - decomposition
  - branches
  - holon-agentic-coder
created_at: 2026-11-11T10:30:00Z
updated_at: 2026-11-12T08:30:00Z
---

## Problem

The first run of Bean 0274 (2026-11-11) decomposed into four sub-intents and its first child failed at Stage 3 with
`remote: ref too long: "refs/heads/I-1794390859-every-flow-stage-uses-the-host-worktree-and-no-clone-url/P-.../E-.../_"`
(`pre-receive hook declined`). A child branch nests the parent plan branch, the child intent slug, its own plan and its
execution branch, and each `P-` and `E-` segment carries the agent and model (`claude-agent-claude-sonnet-5-5`). The
failing execution branch was 282 characters (293 with `refs/heads/`).

**Measured limit (2026-11-11, throwaway branches pushed to and deleted from the harness repository):** GitHub accepts a
full ref name of up to 255 characters including `refs/heads/` and rejects 256 and above. A branch name can therefore be
at most 244 characters, and an execution branch must be at most 235 so that its `/calibrated` sibling (9 characters
longer than `/_`) also fits. The executor then exits with code 1 and the whole flow stops, although the work was done
(the patch is printed as "UNPUSHED EXECUTION PATCH").

## Action

Run through the Holon flow (`todo/intent-0275-refcap.json`). The engine measures every branch name it is about to
create, including the `/calibrated` suffix and the `refs/heads/` prefix, and keeps it under a documented limit by
shortening the segments it controls (the intent slug, the child slugs, the agent and model labels) with a stable,
collision-free abbreviation recorded in the ledger row, and fails at Stage 1 with a clear message when the name cannot
fit. Hermetic tests build the failing name and assert the cap.

## Workaround

Give decomposable intents a very short slug (8 characters kept the Bean 0274 names under the limit).

## Resolution

Delivered via [PR #166](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/166) and merged into `main`
(`0528a63`, 2026-11-11T21:18Z), through the 5-stage flow (`claude-agent` / `claude-sonnet-5-5`, intent slug `refcap`),
followed by a harness `pr-review-loop`.

- **Deliverable**: `ref_names.py` holds one limit (255 characters, `refs/heads/` included) and one builder that checks
  every branch name the engine creates as if it ended in `/calibrated`. Names that fit are unchanged; longer ones are
  shortened deterministically with a stable digest, original labels are recorded in the ledger rows, a name that cannot
  fit fails at Stage 1, and a rejected push is reported by name. Documented in `docs/git_flow.md` and
  `docs/ledger_schema.md`.
- **Review**: the flow's engine review took 10 iterations (calibration predicted EV 42.72, actual -24.31, delta -67.03).
  After syncing with `main` (Beans 0160 and 0274 had merged, which removed the executor's container-side unpushed-work
  reporting and moved its push error to `flow/host_remote.py`) the harness loop ran 2 iterations: iteration 1 found
  important issues that the resolver fixed (two nits rejected with reasons), iteration 2 was unanimous 3/3 with 0
  findings, read from the on-disk reports. CI 11/11 at `16e2f71`.
- **Origin**: found when the first run of Bean 0274 failed pushing a 282-character child branch; the limit (255
  accepted, 256 rejected) was measured against GitHub with throwaway branches on 2026-11-11 and is documented in
  `.agents/rules.md`.
