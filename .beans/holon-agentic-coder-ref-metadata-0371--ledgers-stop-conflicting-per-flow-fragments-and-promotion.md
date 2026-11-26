---
# holon-agentic-coder-ref-metadata-0371
title: "Ledgers stop conflicting: per-flow pending ledger fragments, promoted into the canonical ledgers on main"
status: completed
type: feature
priority: critical
tags:
  - flow
  - ledger
  - merge-conflicts
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-23T06:40:00Z
updated_at: 2026-11-26T04:02:30Z
---

## Problem

Every flow appends rows to the same three files (`holon-knowledge/ledger/{intents,plans,executions}.jsonl`) and to
`holon-knowledge/kb/failure_modes/index.json`. Any two PRs open at the same time therefore conflict as soon as one
merges, even when their code is disjoint. On 2026-11-23 alone, #244, #248 (twice), #250, #251 and the bean 0191 child 3
branch all went `CONFLICTING`/`DIRTY` against `main` this way:

- Each conflict forces a merge of `origin/main` into the PR branch, which moves the reviewed head, voids or questions
  the approval, re-triggers CI, and (with the PR #250 CI gate) can restart Stage 4. Stage 5 calibration has also
  miscounted files merged in this way (bean 0369).
- Ledger-only conflicts are resolved by hand or by `resolve_known.py` interleaving rows by `created_at`. It is
  mechanical but costs a subagent run, a push and a CI cycle per PR per merge to `main`.
- `executions.jsonl` is 7,400+ lines and grows with every review iteration, so it collides with every other flow.
- `kb/failure_modes/index.json` is a single JSON object whose closing brace moves on every append, so it always
  conflicts too.

## Goal

Two concurrent flows never conflict on ledger or KB index files, whatever order their PRs merge in. The three canonical
append-only ledgers on `main` keep their meaning and remain the provenance record.

## Proposed design (the maintainer's direction: a directory per flow plus promotion)

1. **Pending fragments on branches.** A flow never writes the canonical `*.jsonl` files. It appends its rows to its own
   file, e.g. `holon-knowledge/ledger/pending/<ledger>/<intent-id>.jsonl` (one file per intent, split children
   included), so no two flows touch the same path. Row format is unchanged; `LedgerLock` still guards each fragment.
2. **Readers see one ledger.** `ledger/query.py` and every reader (calibration, admission, in-flight, reconcile, touch
   set, ...) read canonical rows plus all pending fragments, merged by `created_at` with stable ordering and
   de-duplication by row id. No caller reads a `.jsonl` path directly. 2a. **Search covers every pending row, merged or
   not (maintainer, 2026-11-23).** Unpromoted rows are useful (what other flows are doing, their failures, their
   findings), so `holon ledger` search/query (`cli/commands/ledger.py`, `ledger/query.py`) reads three sources and
   labels each row with where it came from:
   - `canonical`: the three ledger files on the current branch;
   - `pending`: fragments on the current branch (merged flows not yet promoted, plus this flow's own rows);
   - `in-flight`: fragments of flows not yet merged, read without a checkout via `git show <ref>:<path>` from open PR
     head branches and local flow worktrees, discovered the same way `flow/in_flight.py` finds in-flight flows (after a
     `git fetch`). A flag (`--in-flight` / `--no-in-flight`) controls this; the source label and the branch name appear
     in the output. Rows are de-duplicated by row id (a promoted row wins over its fragment copy). In-flight rows are
     unreviewed, so they are for search, admission/overlap checks and the KB/failure-mode lookup only: calibration EV,
     outcome and touch-set metrics never count rows that are not on the flow's own branch.
3. **Promotion by CI on every push to `main` (maintainer decision, 2026-11-23: option (a)).** A GitHub Actions workflow
   triggered on `push` to `main` runs `holon ledger promote`: it folds every pending fragment into the canonical ledgers
   in `created_at` order, deletes the promoted fragment files, and pushes one ledger-only commit to `main` as a bot
   identity. Requirements:
   - Promotion is idempotent: re-running it on an already promoted tree changes nothing, and a row already in a
     canonical ledger is never appended twice.
   - The commit touches only `holon-knowledge/ledger/**`; the workflow fails rather than push anything else.
   - The workflow does not re-trigger itself (skip when the push is its own promotion commit) and uses a concurrency
     group so two pushes to `main` never promote in parallel; a push race is retried after a fetch/rebase of the
     ledger-only commit.
   - It authenticates with a dedicated bot token or GitHub App that branch protection allows to push to `main`, scoped
     to contents write on this repository only. Setting up that token and the protection bypass is a maintainer step,
     not something the flow does.
   - **Batched, not per merge (maintainer, 2026-11-23).** The workflow runs on every push to `main` but promotes only
     when at least `HOLON_LEDGER_PROMOTE_EVERY` merged flows (default 10) have pending fragments on `main`, plus a daily
     scheduled run and a manual `workflow_dispatch` so a quiet week still compacts. With per-flow fragments, in-flight
     PRs never conflict with each other or with a promotion commit (promotion only appends to the canonical files, which
     flows no longer write, and deletes fragments of already merged flows), so batching changes only how often `main`
     gets a bot commit, not whether PRs conflict. Fewer promotion commits mean fewer CI runs on `main` and fewer "branch
     out of date" updates if branch protection requires up-to-date branches.
   - If promotion fails, `main` still works: readers already see pending fragments (point 2), so a failed or delayed
     promotion never loses or hides rows.
4. **KB index removed, derived on read.** Nothing in production reads `kb/failure_modes/index.json` (only
   `knowledge/wisdom.py::_update_directory_index` writes it; tests assert it exists; docs describe it), and every field
   it holds (`kb_id`, `file`, `kb_type`, `status`, `created_ts`, `tags`) is already in the matching
   `KB-failure-<id>.json`. Its top-level `updated_ts` changes on every write, so it conflicts on every PR. Remove the
   writer, `git rm` the `index.json` files under `kb/` and `wisdom/`, ignore them, and add a `load_index(subfolder)`
   that globs the entry files when a lookup is needed (optionally a `holon kb index` command writing an untracked copy).
   Update the tests and `docs/knowledgebase_schema.md` / `docs/wisdombase_schema.md`. This part needs no promotion and
   can ship first as its own small flow.
5. **Migration.** Existing canonical ledgers stay as they are. In-flight branches that still append to the canonical
   files are handled once: promotion/reconcile accepts rows in either place and de-duplicates.

## Also seen: add/add conflicts on KB entry files (2026-11-23, PR #252)

Removing `index.json` (Bean 0373) does not remove every KB conflict. Two flows that hit the same failure mode both
create `holon-knowledge/kb/failure_modes/KB-failure-<fingerprint>.json` with the same id and content that differs only
in timestamps (`created_ts`, `updated_ts`); merging `main` then reports an add/add conflict per file (16 on PR #252).
`resolve_known.py` only strips `created_ts`, so these still need judgement today. In scope for this bean: either write
KB entries deterministically for a given fingerprint (no wall-clock fields in the file; timestamps live in the ledger
row), or route new KB entries through the same per-flow pending area and let promotion de-duplicate by id. Until then,
teach `resolve_known.py` to settle timestamp-only add/add KB files by keeping the target branch's copy.

## Decisions

- **Promotion trigger: (a), a CI job on each push to `main`** (maintainer, 2026-11-23). Rejected: (b) promotion in the
  next flow's Stage 1, which leaves fragments on `main` between flows and puts ledger churn into unrelated PRs; (c) no
  promotion, which redefines the ledgers as directories.
- **Still to do before the flow runs:** the maintainer creates the bot token / GitHub App and allows it past branch
  protection for `main`; rule 14 in `.agents/engineering-rules.md` is reworded to say per-flow pending fragments are the
  same three ledgers split by flow (not auxiliary ledgers) and that only the CI promotion job writes the canonical
  files.
- **Considered and not enough on its own:** `.gitattributes` `*.jsonl merge=union`. It fixes local merges of append-only
  files, but GitHub's server-side mergeability check does not apply custom merge drivers, so PRs would still show
  `CONFLICTING`. It may still be added for local merges.

## Acceptance criteria

- `holon ledger` search returns canonical, pending and in-flight rows with a source label and branch; an in-flight row
  from another open PR appears without checking that branch out, and disappears once its fragment is promoted (shown
  once, as `canonical`). Calibration ignores in-flight rows (test with a fixture that has all three sources).
- Two flows started from the same `main`, each writing intent, plan, execution, review and calibration rows, produce PRs
  that merge in either order with no conflict on any file under `holon-knowledge/`.
- Every ledger reader returns the same rows, in the same order, before and after promotion.
- The promotion workflow runs on a push to `main`, commits only ledger files, does not re-trigger itself, and a second
  run on the same tree is a no-op.
- Promotion is idempotent and loses no row (property test: random fragment sets and promotion orders; the union of rows
  is preserved and ordered by `created_at`).
- `kb/failure_modes/index.json` is no longer written by flows; the index is derived from the KB files.
- Calibration and admission produce identical results on a fixture that has rows in both canonical and pending form.
- `resolve_known.py` and the `resolve-conflict` skill no longer need a ledger interleave for new flows (kept only for
  legacy branches).
- Applies to both `holon-agentic-coder` and `holon-coherence`.

## Delivery

Through the 5-stage Holon flow on `holon-agentic-coder` (then `holon-coherence`), after the maintainer settles the
decisions above. Keep the intent text free of harness paths and bean ids. Update rule 14 in
`.agents/engineering-rules.md` and the `resolve-conflict` skill in the harness to match. Likely overlaps with bean 0369
(calibration reads the ledger), so run it after 0369 merges or with `--allow-overlap` and a narrow scope.

## Measured (self-improvement audit 2026-11-24)

What ledger conflicts cost in the period 2026-11-21 to 2026-11-24 (scripts in the git-ignored
`todo/self-improvement-audit-2026-11-24/`):

- 57 of 422 pipeline runs were on heads produced by a merge of `main` into the flow branch; the conflict gate merges
  only when the pull request is `CONFLICTING` or `DIRTY`, and with append-only canonical ledgers almost every merge of
  another pull request makes it so.
- 17 full review iterations (127 minutes) ran because of a conflict with `main` or a merge of `main`; 12 Stage 4 runs
  ended "CI signal suppressed: pull request has merge conflicts".
- 12 Stage 3 starts stopped "merging origin/main ... after the admission wait conflicts in holon-knowledge/ledger/" (10
  in `intents.jsonl`, 2 in `executions.jsonl`; Bean 0391).
- One hygiene failure was an invalid ledger after a merge (`jq: parse error`, run 45182713288, PR #263).

This bean would remove most of these; it is the largest single source of churn after bookkeeping-only pipeline runs
(Bean 0403).

## Audit evidence, 2026-11-24T12:58Z (self-improvement audit, fifth merge)

- PR #272 (Bean 0403) was put into conflict three times in 105 minutes (merges of PR #269, #270 and #274); every overlap
  with those PRs was `holon-knowledge/ledger/{intents,plans,executions}.jsonl` only.
- PR #275 (Bean 0405) was opened at 12:39:51Z and was `DIRTY` within six minutes, again on the three ledgers only (PR
  #274 merged at 12:45:46Z).
- Each conflict cost a halted Stage 4, a hand merge of `origin/main` by an agent and a relaunch, plus up to one full
  review iteration on the conflicting head (26 minutes on PR #272).

## Resolution

Delivered via [PR #314](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/314) and merged into `main`
(`4e35895`), with its child PRs [#310](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/310) (`ba5e090`),
[#311](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/311) (`0a7f690`),
[#312](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/312) (`153b608`) and
[#313](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/313) (`89ad0fd`) merged into the plan branch
first:

- **Key Architectural Deliverables**: per-flow pending ledger fragments under
  `holon-knowledge/ledger/pending/<ledger>/<root-intent-id>.jsonl`; every ledger append routed through the ledger
  package (#311); a merged reader (`ledger/fragments.py`, `ledger/merged.py`, `ledger/order.py`) used by every
  canonical-ledger reader, with canonical rows winning on duplicate ids (#310); `holon ledger promote` with
  `HOLON_LEDGER_PROMOTE_EVERY` batching, idempotent and additions-only (#312); `.github/workflows/promote-ledger.yml` on
  push to `main`, daily schedule and `workflow_dispatch`, a green no-op until the `HOLON_LEDGER_BOT_TOKEN` secret exists
  (#313).
- **Out of scope (separate flows)**: removal of `kb/failure_modes/index.json`, the one-time chronological re-sort of the
  canonical ledgers, and the hygiene check on moved ledger rows.
- **Verification & Tests**: unit, CLI and property tests for promotion; a guard test that fails if any append writes a
  canonical ledger file; a two-branch test that merges in either order with no conflict under `holon-knowledge/`; a
  structural parsed-YAML test for the workflow.
- **Holon Flow Traversal**: all 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed for the
  parent and each child intent; review iterations were run on each child PR before merge.
- **Still a maintainer step**: the `HOLON_LEDGER_BOT_TOKEN` secret and the branch-protection bypass for `main` are not
  yet set, so promotion stays a no-op until they are.
