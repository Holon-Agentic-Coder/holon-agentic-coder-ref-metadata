---
# holon-agentic-coder-ref-metadata-0058
title: "Make flow-produced markdown converge on prettier so the hygiene job stops failing"
status: todo
type: bug
priority: normal
tags:
  - flow
  - ci
  - hygiene
  - prettier
created_at: 2026-09-28T05:10:00Z
updated_at: 2026-09-28T05:10:00Z
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
