---
# holon-agentic-coder-ref-metadata-0411
title: "Harness instructions contradict each other on runner switching, model ladders and file size"
status: todo
type: bug
priority: high
tags:
  - harness
  - instructions
  - agents
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-25T05:45:00Z
---

## Why

Subagents read different files and get different answers. The audit protocol asks for instructions that contradict each
other.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

1. **Switching runner on a quota limit.** `.agents/holon-flow.md` ("Cross-Runner Fallback ... automatically switch
   `--agent`"), `.agents/instructions.md` ("Cross-Runner Continuation") and `.agents/workflows.md` (same) say switch
   automatically; `.agents/skills/holon_flow/SKILL.md` ("No Cross-Runner Switch: never switch `--agent` ... on your
   own") says never. The maintainer's word is the skill's: stay on the Claude ladder and ask before switching runner.
2. **Model ladders written out in eight places** (`AGENTS.md`, `.agents/holon-flow.md`, `.agents/instructions.md`,
   `.agents/workflows.md`, `.agents/coordination.md`, `.agents/subagents.md`, `.agents/skills/holon_flow/SKILL.md`,
   `.agents/skills/pr_review_loop/SKILL.md`). The Antigravity default changed from `gemini-4-argon` to `gemini-4-neon`
   on 2026-11-24 and had to be edited in each; the next change will miss one.
3. **Which runner a flow uses by default.** `AGENTS.md` says `antigravity-agent` for all Holon coding tasks; the Claude
   ladder in `.agents/holon-flow.md` and the flow practice of 2026-11-23/24 put `claude-fable-5-2` first. A subagent
   cannot tell which applies.
4. **File size.** `.agents/engineering-rules.md` rule 15 calls 200 lines "a recommended guideline ... rather than a
   rigid hard rule"; the module budgets are enforced and force splits, and the target's review prompt flags any growth
   of a file over 1,000 lines as Important (25 findings in the period). Three different limits.

## Proposed change

- One canonical section per rule (runner and model ladder in `.agents/model-tiers.md` or `.agents/holon-flow.md`, file
  size in `.agents/engineering-rules.md`); every other file links to it and states nothing of its own.
- Runner switching: write the maintainer's rule (ask first) in the canonical place and delete the automatic-switch text.
- File size: state the three limits as they are enforced (200-line guideline, enforced module budgets, no growth over
  1,000 lines) in rule 15.

## Expected gain

Fewer wrong launches and wrong fallbacks by subagents; one edit per future change instead of eight.

## Cost

Small harness-only edit.

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- Item 2 happened. `AGENTS.md` (hard rule, committed) still says "`antigravity-agent` with `gemini-4-argon` ... then
  `gemini-4-hydrogen` → `gemini-3.8-flash`" (maintainer, 2026-11-22). `.agents/holon-flow.md` lines 67 to 68 say
  `gemini-4-neon` first, then `gemini-4-argon`. Every Antigravity flow in the period ran `gemini-4-neon` (ledger `model`
  and `review_model` fields on #288 to #307).
- The same split shows up across sessions: rules held only in Claude Code's private memory never reach the Antigravity
  session (Bean 0459).

- Progress (2026-11-25): aligned with the skill's "No Cross-Runner Switch" and the maintainer's rule of 2026-11-23 (stay
  on the runner's ladder, ask before switching): `.agents/holon-flow.md`, `.agents/instructions.md`,
  `.agents/workflows.md`, `.agents/coordination.md` section 5 and the PR driver note in the review-loop skill.

- Item 3 follow-up (2026-11-26): Bean 0483 measures runner and model wall time on comparable flows to choose the
  default.
