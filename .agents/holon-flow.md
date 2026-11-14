# Holon Flow Rules

Details of the sole change path (Holon flow), its model and runner fallback ladders, and the rule to always drive it
with `holon flow`. Moved verbatim from `AGENTS.md`.

---

## 🔒 Sole Change Path: The Holon Flow

> [!IMPORTANT] **Every change to a target codebase (`holon-agentic-coder` or `holon-coherence`) MUST be produced by the
> 5-stage Holon flow.** No agent or developer may hand-author, hand-patch, or directly commit changes to
> `holon-agentic-coder` or `holon-coherence` outside the flow lifecycle. Invoking `holon` inside either target
> repository's worktree dynamically resolves `remote.origin.url` via `resolve_target_repo_url()`, driving the target
> repository's `holon-knowledge/ledger/` provenance pipeline.

The lifecycle is a single pipeline, not a menu. A change is only "done through the flow" when it has traversed all of
its stages:

| #   | Stage          | Invocation (manual form)                                                                      | Artifact                                                                           |
| --- | -------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1   | Intent         | `holon intent <intent.json>`                                                                  | `I-{timestamp}-{slug}/_` + `holon-knowledge/ledger/intents.jsonl`                  |
| 2   | Plan           | `holon plan <intent_branch>`                                                                  | `I-.../P-{ts}-{agent}-{model}/_` + `plans/P-*.md` + `plans.jsonl`                  |
| 3   | Execute        | `holon execute <plan_branch>`                                                                 | `I-.../P-.../E-{ts}-{agent}-{model}/_` + `holon-knowledge/ledger/executions.jsonl` |
| 4   | PR review loop | `holon review <execution_branch>` (+ `pr-review-loop` ensemble/resolver when fixing findings) | Consensus approval posted to the PR + `executions.jsonl` (`ACT-REV`/`ACT-POST`)    |
| 5   | Calibration    | `holon calibrate <execution_branch>` (Bean 0038)                                              | `/calibrated` branch + `plans/P-*_calibration.md` (also included in PR diff)       |

**Ordering of the merge boundary**: stage 5 (Calibration) is a **pre-merge** stage, matching `STAGE_ORDER` in
`sandbox_executor/flow.py` (intent -> plan -> execute -> review -> calibrate). Run the review loop to consensus
approval, calibrate, and only then stop and request the merge -- never calibrate after it, because merging a flow PR
consumes the `E-...` execution branch that calibration reads.

**Calibration branch and PR inclusion**: Running calibration creates the audited `/calibrated` branch
(`I-.../P-.../E-.../calibrated`), which must be created and pushed. **For Pull Requests, the calibration report
(`plans/P-*_calibration.md`) MUST ALSO be included in the PR** (by fast-forwarding or merging the calibration commit
into the PR head execution branch `.../_` and pushing to `origin`) so that the calibration report appears in the PR diff
and is preserved in `main` history when merged. Merging itself stays human-only (see "🔒 PR Merging — Human-Only"
below).

**Always use `holon flow` to drive changes.** Changes to target codebases MUST always be executed using the unified
`holon flow <intent.json>` runner. Never use ad-hoc wrapper scripts (such as `holon-stage.sh`), and do not execute
disconnected manual stage commands when authoring or driving tasks. `holon flow` is the canonical, self-contained
orchestrator for the entire 5-stage lifecycle. When resuming an in-flight pipeline after fixing a blocker, timeout, or
stepping down model tiers, always resume through `holon flow <intent.json> --from-stage <stage>` or
`holon flow --checkpoint <path-to-checkpoint.json>`.

**Consequences for agents:**

- Changes are authored by the sandboxed role agents inside the containerised plan/execution branches and recorded in the
  append-only ledgers. The ledgers, not the agent's word, are the system of record.
- Host-side worktrees (`apps/<project>/{branch}`) exist to **build images, inspect code, run verification, and operate
  the harness** -- they are not a change-authoring surface. Editing `holon-agentic-coder` or `holon-coherence` source in
  a worktree outside the flow bypasses intent provenance, plan metrics, EV accounting, and the execution ledger, and is
  therefore prohibited.
- Skipping a stage is not permitted. If a stage cannot run (missing image, failed agent, unreachable remote), the change
  is **blocked**: report the blocker instead of hand-applying the diff as a workaround.
- **Automatic Model & Runner Fallback on Credit / Quota Exhaustion**: If a stage or subagent fails due to model credit
  exhaustion, session quota limits, or rate-limit caps (e.g. `You've hit your session limit`, `insufficient_quota`,
  `RESOURCE_EXHAUSTED`, or HTTP 429/quota errors), **do not stop or block** as long as a lower-tier model or alternate
  configured runner still has available credit. Automatically step down the fallback ladder and **continue the flow from
  the current stage/checkpoint** (reusing any already-pushed `I-.../_`, `P-.../_`, or `E-.../_` branch):
  - **Claude (`claude-agent`) fallback ladder**: `claude-fable-5` (or `fable`) $\rightarrow$ `claude-opus-5-5` (or
    `opus`) $\rightarrow$ `claude-sonnet-4-6` (or `sonnet`) $\rightarrow$ `claude-haiku-4-5` (or `haiku`). Fable is the
    preferred top tier for flow stages (maintainer, 2026-11-05); `holon` passes `--model` through to the runner
    verbatim, so no engine change is needed.
  - **Antigravity (`antigravity-agent` in `holon` CLI) fallback ladder**: `gemini-3.8-pro-high` (or `gemini-3.8-pro`)
    $\rightarrow$ `gemini-3.8-flash-medium` $\rightarrow$ `gemini-3.8-flash`.
  - **Antigravity (`invoke_subagent` in AGY runtime) fallback ladder**: `Model: "inherit"` / `"pro"` $\rightarrow$
    `"flash"` $\rightarrow$ `"flash_lite"`.
  - **Cross-Runner Fallback**: If all model tiers on the active runner (`claude-agent` or `antigravity-agent`) share an
    exhausted account-wide session limit, automatically switch `--agent` to the other runner (`antigravity-agent` or
    `claude-agent`) at its highest available tier with credit and continue the remaining flow stages on the existing
    flow branch.
- The only permitted exception is an explicit, unambiguous user instruction to make a specific edit outside the flow,
  and that exception must be named in the commit message and in the bean summary.

**Harness exception & operational branches (control plane only).** The `holon-agentic-coder-ref-metadata` control plane
itself (`.beans/`, `.agents/`, `AGENTS.md`) is the coordination harness rather than a flow-managed target repository.
Those harness files stay directly editable. Furthermore, **harness branches (such as `docs/harness-YYYYMMDD` or task
tracking branches) exist for day-to-day operations and do not need to be merged into `main` frequently**. They serve as
the continuous operational record and living logbook of work done across sessions (tracking bean states, updating triage
matrices, refining agent guidelines, and logging task history). Agents must not feel pressured to raise PRs or request
merges for regular harness updates; merging harness branches into `main` is an infrequent maintainer checkpoint.

---

9. **Route Every Change Through the Flow & Always Use `holon flow`**: Produce all `holon-agentic-coder` and
   `holon-coherence` changes via the five-stage Holon flow (intent -> plan -> execute -> PR review loop -> calibration)
   rather than hand-authored host-side edits, and calibrate before requesting the merge. **Always use the unified
   `holon flow <intent.json>` runner directly** (or `--from-stage` / `--checkpoint` when resuming); never use ad-hoc
   wrapper scripts like `holon-stage.sh` or manual disconnected stage commands. See
   [🔒 Sole Change Path: The Holon Flow](#-sole-change-path-the-holon-flow).
