---
# holon-agentic-coder-ref-metadata-0058
title: "Make flow-produced markdown converge on prettier so the hygiene job stops failing"
status: completed
type: bug
priority: normal
tags:
  - flow
  - ci
  - hygiene
  - prettier
created_at: 2026-09-28T05:10:00Z
updated_at: 2026-10-04T07:55:00Z
---

Every Holon flow PR fails the `hygiene` job on `npx --yes prettier@3.8.4 --check "**/*.md"` because the intent, plan and
execution artifacts the agents commit are not prettier-formatted. That part is expected work for the resolver. The part
that is not expected: **formatting once does not fix it.**

## Measured evidence (Bean 0019 slice B, PR #61)

- `npx --yes prettier@3.8.4 --write plans/P-1790564277-antigravity-agent-gemini-3.8-flash-medium.md` reported success
  and changed 303 lines, and `prettier@3.8.4 --check` on the same file immediately reported
  `Code style issues found in the above file` again.
- A second `--write` pass moved 8 more lines, after which `--check` passed. The formatter is therefore not idempotent on
  the markdown the planner emits, so a single `--write` (what a resolver naturally runs, and what the loop's rule
  "re-run `npx prettier --write \"**/*.md\"`" prescribes) leaves the branch red.
- PR #61 commit `6d18890` was pushed with a formatted-but-still-failing plan file; `16e530a` converged it and hygiene
  went green. PR #60 hit the same wall on its first CI run.

## Why it matters

The failure is charged to the PR instead of the generator, so every flow run spends a review iteration on formatting,
and the loop has learned to run prettier blindly rather than to convergence. Worse, the cost is invisible to whoever
changes the plan prompt: the emitted markdown simply never reaches a fixed point.

## Candidate remedies (needs an owner decision)

1. Make the formatter run converge: `prettier --write` in a bounded loop (2-3 passes) until `prettier --check` exits 0,
   then fail the stage loudly if it cannot converge. Put it in the flow's execute stage and in the resolver rule.
2. Fix the generator so its output is a prettier fixed point in one pass -- identify the construct that oscillates
   (table alignment or nested blockquote/heading nesting in the planner template are the prime suspects) and stop
   emitting it.
3. Minimum viable: have `holon` run a convergence pass over changed markdown right before committing a plan or execution
   artifact, so a flow branch never leaves the machine red.

## Notes

- Target repository: `holon-agentic-coder`, `apps/sandbox-executor` (planner prompt/template plus the flow/CLI commit
  path) and the `.github/workflows` hygiene definition.
- Discovered while closing Bean 0019; see its closeout section, deviation 2.
- Changes must go through the flow, not a host-side hand edit.

## Resolution

Resolved via the full 5-stage Holon flow:

1. **Stage 1 (Intent)**:
   - Intent created on branch `I-1791097634-converge-prettier-on-flow-produced-markdown/_`.
   - Recorded in `holon-knowledge/ledger/intents.jsonl`.
2. **Stage 2 (Plan)**:
   - Plan created on branch
     `I-1791097634-converge-prettier-on-flow-produced-markdown/P-1791097643-antigravity-agent-gemini-3.8-flash-medium/_`.
   - Artifact `plans/P-1791097643-antigravity-agent-gemini-3.8-flash-medium.md` recorded in `plans.jsonl`.
3. **Stage 3 (Execute)**:
   - Execution completed on branch
     `I-1791097634-converge-prettier-on-flow-produced-markdown/P-1791097643-antigravity-agent-gemini-3.8-flash-medium/E-1791098020-antigravity-agent-gemini-3.8-flash-medium/_`.
   - Core implementation:
     - `apps/sandbox-executor/src/sandbox_executor/formatting.py`: Added `converge_prettier` utility with bounded
       convergence loop (default `max_passes=2`), `is_prettier_available` guard, 30s timeout, non-existent target
       filtering, and fail-safe logging without aborting pipeline flow.
     - Formatter integration across all stages: `planner.py` (formats `plans/P-*.md`), `executor.py` (formats
       `executions/E-*.md`), `calibration.py` (formats `plans/P-*_calibration.md`), and `flow.py` (post-calibration
       sweep).
     - Generator prompt hardening: Updated `planner.template.md`, `executor.template.md`, and `scaffold.py` to enforce
       code-span backtick wrapping for mathematical and metric formulas (e.g. `EV = 0.98 * 85.0`), eliminating
       CommonMark italic delimiter oscillations.
     - Added comprehensive unit and integration tests: `test_formatting.py`, `test_planner.py`, `test_executor.py`,
       `test_calibration.py`, `test_flow.py`.
   - Artifact `executions/E-1791098020-antigravity-agent-gemini-3.8-flash-medium.md` recorded in `executions.jsonl`.
4. **Stage 4 (PR Review Loop)**:
   - Opened PR [#62](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/62).
   - Formatted execution record with prettier (`1b91f7c`).
   - GitHub CI ran 10/10 checks: **ALL PASSED 100% GREEN** (Hygiene, CodeQL, Make build macOS/Ubuntu, Unit Tests
     macOS/Ubuntu, Integration Tests).
   - 3-agent ensemble review (`pr-reviewer`): Unanimous approval (3/3 `APPROVED`, 0 Critical, 0 Important, 0 Nit).
   - Consensus approval posted to PR #62 comment stream.
5. **Stage 5 (Calibration)**:
   - Executed `holon calibrate` on execution branch.
   - Generated calibration report `plans/P-1791097643-antigravity-agent-gemini-3.8-flash-medium_calibration.md` on
     branch
     `I-1791097634-converge-prettier-on-flow-produced-markdown/P-1791097643-antigravity-agent-gemini-3.8-flash-medium/E-1791098020-antigravity-agent-gemini-3.8-flash-medium/calibrated`
     and pushed to remote.
   - EV metrics: Predicted EV 78.01, Actual EV 81.70 (ΔEV: +3.69).
   - Added `plans/P-1791097643-antigravity-agent-gemini-3.8-flash-medium_calibration.md` directly to PR #62 branch
     (`22168ad`) per user instruction so calibration is visible in the pull request diff.
6. **Merge Boundary**:
   - Preserved strict human-only PR merge constraint: halted with consensus approval and calibration complete.
   - PR #62 is ready for human merge at https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/62.
