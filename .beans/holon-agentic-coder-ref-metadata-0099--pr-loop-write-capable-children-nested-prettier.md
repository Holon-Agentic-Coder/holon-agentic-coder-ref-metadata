---
# holon-agentic-coder-ref-metadata-0099
title: "Require write-capable children for pr-review-loop passes and scope Prettier to the target repository"
status: completed
type: task
priority: high
tags:
  - pr-review-loop
  - subagents
  - local-llm
  - prettier
  - auditability
created_at: 2026-10-16T01:11:55Z
updated_at: 2026-10-16T03:03:00Z
---

Three defects in the `pr-review-loop` protocol surfaced while driving Bean 0097 to convergence on `holon-coherence` PR
#19. All three were absorbed by the orchestrator at the time; none is written down anywhere, so the next loop will hit
them again.

## Summary

1. **A review pass on a child that cannot write files is not a vote.** The first reviewer-1 cast on PR #19 was
   dispatched to pi's `reviewer` agent, which has no file-write tool. It returned a trailer block (`COMMENT 0/0/1`) with
   **no report file anywhere on disk** — the vote was unauditable (the finding it counted was never recorded, so no
   resolver could disposition it) and had to be discarded and re-cast on a write-capable child. The skill demands a
   durable report per pass (principle 10) but nowhere states that the child must possess a write tool, and
   `LOCAL_RUNTIME.md` §4 shapes prompts for a local backend without saying which agent type is admissible. State the
   requirement, state that a verdict with no artifact is `DEAD` and must be re-cast, and state the probe for admissible
   agent/model names (an intentionally invalid `agent`/`model` value returns the valid list instead of launching).
2. **On-disk trailer beats the child's final message, and the conflict must be reported.** Iteration 1 reviewer 3
   replied `important=1` while its report trailer on disk read `IMPORTANT: 0`. `LOCAL_RUNTIME.md` §5 says to read the
   report first, but does not say what to do when the two disagree: rule it explicitly — the file is the record, the
   divergence is logged in the loop history, and neither number may be silently reconciled to the other.
3. **Prettier resolves the harness config from inside a nested target worktree.** The flow checkout
   `apps/holon-coherence/<branch>/` lives inside the harness checkout, so `prettier --find-config-path` resolves
   `holon-agentic-coder-ref-metadata/.prettierrc.json` (printWidth 100, `proseWrap: always`), which `holon-coherence`
   does not carry. A repo-wide `prettier --write "**/*.md"` in such a worktree reflows unrelated documents and the CI
   `hygiene` job then disagrees with the local format. Two runs on PR #19 (`a799a20`, `c1b9c9f`) had to work around this
   by hand. Document the hazard and the safe form: format **only the changed files** with the target repository's own
   config (or `--no-config` when it has none), then verify `git diff --stat` lists no unintended file.

## Targets

Harness-only (the control-plane exception in `AGENTS.md`: the flow cannot reach this repository), so this is authored
directly in the harness checkout, exactly as Beans 0057, 0063 and 0081 were.

- `.agents/skills/pr_review_loop/SKILL.md` — principles 9, 10 and 11, and the Phase A / Phase C subagent contracts.
- `.agents/skills/pr_review_loop/LOCAL_RUNTIME.md` — §4 (prompt shaping) and §5 (attrition handling).
- `.agents/workflows.md` and/or `.agents/rules.md` — the nested-worktree formatting rule, if it belongs beside the
  worktree rules rather than only in the skill.

## Acceptance Criteria

- [x] The skill states that every review, consensus and resolution child MUST be able to write its report file, and that
      a returned verdict with no artifact is recorded `DEAD`, excluded from the vote count, and re-cast.
- [x] The skill states how to discover admissible child agent and model identifiers on a given harness before the first
      fanout, instead of guessing and losing a dispatch.
- [x] The skill states that when a child's final message contradicts its on-disk trailer block, the file governs and the
      divergence is recorded in `<repo>_pr<N>_loop_history.md`.
- [x] Formatting guidance covers the nested-worktree case: target-repo config only, changed files only,
      `git diff --stat` verified before committing.
- [x] Both skill files pass `npx prettier --check`, and the change is squashed onto a harness branch pushed without a
      merge.

## Resolution Summary

All acceptance criteria satisfied directly in the harness control plane:

1. **`SKILL.md` (Principles 9, 10, Phase A, B, C Contracts)**:
   - Principle 9 now mandates file-writing tools (`write_to_file`, `replace_file_content`, etc.) for every reviewer,
     consensus, and resolver pass; verdicts without an on-disk report artifact are marked `DEAD` and re-cast.
   - Principle 9 documents upfront dry-probe discovery for admissible agent types and model identifiers (`__probe__`).
   - Principle 10 mandates that an on-disk report trailer block strictly governs over a conflicting child chat message,
     with any divergence logged in `<repo>_pr<N>_loop_history.md`.
   - Phase A, Phase B, and Phase C generic subagent contracts updated to require write-capable child types (e.g. AGY
     `TypeName: "self"`).
2. **`LOCAL_RUNTIME.md` (§4, §5)**:
   - Added write-capable agent type rule and upfront identifier discovery probe.
   - Added `DEAD` vote exclusion rule and on-disk trailer precedence over chat messages.
3. **`workflows.md`, `rules.md`, and `AGENTS.md`**:
   - Added **Invariant 13** in `rules.md` and updated Task Completion in `workflows.md` and checklist item 6 in
     `AGENTS.md`: nested worktrees (`apps/<project>/<branch>/`) must format only changed files using the target
     repository's configuration (or `--no-config`) to avoid resolving parent harness `.prettierrc.json`.
4. **Verification**:
   - `npx prettier --check` clean across all modified files.

## Notes

- Evidence lives in `.subagent/holon-coherence_pr19_loop_history.md` and `.subagent/holon-coherence_pr19_state.json`
  (`passes[]` records the discarded first cast; `residual_risks[]` records the write-capability constraint discovered at
  runtime).
- Precedent for the shape of this bean: 0081 (serial dispatch on local runtimes), 0057 (namespaced artifacts), 0063
  (durable resume state). This bean continues that line: the loop's guarantees are only as good as the artifact each
  pass leaves behind.
