---
# holon-agentic-coder-ref-metadata-0081
title: "Serialise the 3-agent PR review consensus when the model runs locally"
status: in-progress
type: task
priority: high
tags:
  - subagents
  - pr-review-loop
  - local-llm
  - coordination
created_at: 2026-10-10T03:20:00Z
updated_at: 2026-10-10T03:20:00Z
---

## Summary

Running the `pr-reviewer` 3-agent ensemble as three concurrent children on a **local** model runtime destabilises the
operator's machine. All children inherit the parent's model, so a fanout of three hits one local inference backend at
once. Observed on this workspace with `PI_PROVIDER=vmlx` / `PI_MODEL=JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M`: six
concurrent reviewer children (three for `holon-agentic-coder` PR #69, three for `holon-coherence` PR #13) all died with
`The model produced reasoning_content but no visible answer and no tool call`, wrote no reports, and pushed the host
into contention.

The process documents said, flatly, "Spawn subagents ... concurrently in parallel", so an agent following the skill had
no way to do the right thing.

## Requirements

1. Add a **dispatch concurrency policy** to `.agents/coordination.md` that classifies the parent's model runtime as
   local / hosted / unknown, with concrete detection signals (Pi `$PI_PROVIDER` / `$PI_MODEL`; `vmlx`, `ollama`,
   `lmstudio`, `mlx`, `llama.cpp`, a `localhost` / `127.0.0.1` model endpoint; ask the operator once when unknown, never
   assume hosted).
2. On a **hosted** runtime keep concurrent fanout as the default. On a **local** runtime, cap LLM-inference children at
   one at a time, launching the next only after the previous terminates. Non-LLM work (builds, `uv sync`, tests, image
   builds) stays exempt and may still run in parallel.
3. Make it explicit that **serial is not singular**: still three separate fresh child contexts, three separate briefs
   and report files, three blind independent votes, no reviewer sees another's output, no collapsing the ensemble into
   one reviewer, no handing earlier votes to later ones. Termination rules, the 3/3 unanimity requirement, trailer
   blocks, the coordination ledger and the resume state are unchanged; only the launch schedule moves.
4. Reference the policy from both skills: `pr-reviewer` step 3 (where the concurrent spawn is prescribed) and
   `pr-review-loop` (new principle plus the Phase B ensemble wording).
5. Fold the rule into the existing attrition principle: a dead local pass is salvaged by relaunching **that** pass,
   never by launching a replacement alongside a live sibling.

## Acceptance Criteria

- `.agents/coordination.md` gains the policy as its own numbered section, and "Parallel Work" under "When to Spawn a
  Subagent" points at it.
- `.agents/skills/pr_reviewer/SKILL.md` step 3 no longer mandates parallel dispatch unconditionally and cross-links the
  policy.
- `.agents/skills/pr_review_loop/SKILL.md` carries the rule as a numbered principle, applies it in Phase B, and the
  salvage bullet forbids a parallel relaunch.
- Cross-links resolve (relative paths from each skill to `coordination.md`), and `npx prettier --check "**/*.md"` is
  clean.
- Behaviour validated by running a real 3-agent consensus sequentially on a local runtime.

## Resolution

Harness-only change (control-plane exception in `AGENTS.md`: the flow cannot edit this repository), so it is authored
directly in the harness checkout rather than through the five-stage flow.

- `.agents/coordination.md`: new section 4 "Dispatch Concurrency: Local vs Hosted Runtimes" (detection table, serial
  rule, serial-is-not-singular guarantee, non-LLM exemption, serial salvage); "Parallel Work" bullet and the Monitoring
  section renumbering updated.
- `.agents/skills/pr_reviewer/SKILL.md`: IMPORTANT note at the top of step 3, and the spawn bullet now reads
  "concurrently on a hosted runtime, one-at-a-time on a local runtime".
- `.agents/skills/pr_review_loop/SKILL.md`: new principle 11 "Serial Ensemble On A Local Model Runtime", Phase B
  ensemble wording, and principle 9's salvage bullet now forbids launching a replacement next to a live sibling.

Validated by re-running the PR #69 and PR #13 consensus reviews one child at a time on this local runtime.
