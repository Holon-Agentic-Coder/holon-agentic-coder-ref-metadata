---
# holon-agentic-coder-ref-metadata-0046
title: "Check ledger, KB, and wisdom across intent, planning, execution, pr review loop, and calibration"
status: todo
type: feature
priority: high
tags:
  - holon-flow
  - knowledge-base
  - ledger
  - wisdom
  - continuous-learning
  - intent
  - planning
  - execution
  - pr-review-loop
  - calibration
---

Incorporate pre-action checks and continuous feedback loops against the **ledger**, **knowledge base (KB)**, and
**wisdom**—both at the **project level** (`holon-knowledge/`) and the **global level** (`~/.holon/wisdom/` or global
knowledge store)—across all five phases of the Holon lifecycle: **Intent**, **Planning**, **Execution (Code Changes)**,
**PR Review Loop**, and **Calibration**.

This ensures agents and developers:

1. Detect whether an issue, bug, or feature has been tackled previously across any project or session.
2. Leverage prior root-cause analyses, validated architectural patterns, and execution history.
3. Avoid repeating known regressions or antipatterns by consulting accumulated wisdom at each lifecycle phase.
4. Prevent recurring PR review findings, applying battle-tested fixes during automated review resolution.
5. Continuously refine approaches to execute tasks faster, better, and with lower token expenditure.

## Dual-Tier Knowledge Architecture

1. **Local / Project Tier (`holon-knowledge/`)**:
   - **Ledger** (`holon-knowledge/ledger/`): `intents.jsonl`, `plans.jsonl`, `executions.jsonl`.
   - **Knowledge Base** (`holon-knowledge/kb/`): Project-specific domain documentation, conventions, and architectural
     rules.
   - **Project Wisdom** (`holon-knowledge/wisdom/`): Repository-specific lessons learned, historical bug post-mortems,
     PR review insights, and plan calibrations.

2. **Global / System Tier (`~/.holon/`)**:
   - **Global Ledger** (`~/.holon/ledger/executions.jsonl` or shared index): Cross-repository index of completed tasks,
     PRs, and execution summaries.
   - **Global Knowledge Base** (`~/.holon/kb/`): Organization-wide engineering guidelines, toolchain conventions, and
     platform standards.
   - **Global Wisdom** (`~/.holon/wisdom/`): Universal insights, agent failure patterns, prompt optimization strategies,
     token-reduction recipes, and cross-project post-mortems.

## Five-Phase Lifecycle Integration

### Phase 1: Intent Formulation & Ingestion (`holon intent`)

- **Action**: Query project and global ledgers (`intents.jsonl`) when an intent is registered.
- **Lookup**:
  - Check for duplicate or overlapping intents across prior sessions and projects.
  - Search global KB and wisdom to determine if this problem domain already has established requirements or historical
    precedents.
- **Outcome**: Attach relevant precedent IDs and initial wisdom recommendations directly to the new intent payload.

### Phase 2: Plan Generation (`holon plan`)

- **Action**: Query local and global `plans.jsonl` and `executions.jsonl` before formulating the execution plan.
- **Lookup**:
  - Retrieve previously successful plan breakdowns for similar intents.
  - Scan wisdom for architectural pitfalls, known failure modes, and scope traps observed in past plans.
- **Outcome**: Inject validated execution strategies, expected token baselines, and historical caveats into the planner
  agent's prompt to produce an optimized, hardened plan.

### Phase 3: Code Change & Execution (`holon execute` / Agent Runners)

- **Action**: Perform pre-change wisdom and ledger verification before modifying code files or invoking tools.
- **Lookup**:
  - Query for prior bugs, regressions, or security vulnerabilities associated with the specific target files or
    functions.
  - Consult wisdom for framework-specific quirks (e.g. macOS vs Linux CLI differences, Docker caching caveats, test
    harness sensitivities).
- **Outcome**: Guard the agent against repeating historical mistakes, ensuring every code change complies with both
  local and global engineering wisdom.

### Phase 4: PR Review Loop (`pr-review-loop` / `pr-reviewer` / `pr-review-resolver`)

- **Action**: Integrate wisdom and ledger checks into both the reviewer consensus evaluation and the resolver fix cycle.
- **Lookup**:
  - **Reviewers (`pr-reviewer`)**: Check PR diffs against accumulated wisdom to identify subtle regressions,
    architectural inconsistencies, and known anti-patterns flagged in past reviews across projects.
  - **Resolvers (`pr-review-resolver`)**: Query wisdom before generating code fixes to apply proven, battle-tested
    solutions rather than superficial or brittle patches that cause review ping-pong.
- **Outcome**: Dramatically decrease PR review iteration counts, prevent recurring review nits, and ensure reviewers and
  resolvers share identical architectural standards.

### Phase 5: Calibration & Continuous Synthesis (`holon calibrate`)

- **Action**: Run post-execution calibration against historical ledger records after PR review loop approval.
- **Lookup**:
  - Benchmark token reduction, tool call counts, and review iteration cycles against prior baseline executions.
  - Identify discrepancies between planned steps and actual execution.
- **Outcome**:
  - Distill novel learnings, unexpected edge cases, and efficiency insights discovered during execution and review.
  - Automatically synthesize and append new wisdom records to both local (`holon-knowledge/wisdom/`) and global
    (`~/.holon/wisdom/`) stores, closing the continuous learning loop.

## Tooling & CLI Integration

- **CLI Commands**:
  - `holon wisdom query "<query>" [--scope local|global|all]`: Semantic and keyword search across ledgers, KB, and
    wisdom.
  - `holon wisdom add --scope [local|global] --tag <tag> "<insight>"`: Manually or programmatically append actionable
    wisdom.
  - `holon flow`: Automatically orchestrates ledger/KB/wisdom queries at each phase (Intent -> Plan -> Execute -> PR
    Review Loop -> Calibrate).
- **Agent Guidelines & Prompts**:
  - Update `.agents/workflows.md`, `.agents/instructions.md`, `.agents/skills/pr_review_loop/SKILL.md`,
    `.agents/skills/pr_reviewer/SKILL.md`, `.agents/skills/pr_review_resolver/SKILL.md`, and agent prompt templates
    (`planner.template.md`, `executor.template.md`, `pr_review_prompt.md`) with explicit requirements to inspect local
    and global wisdom prior to generating plans, executing code changes, and conducting PR reviews or resolutions.

## Verification & Acceptance Criteria

- [ ] `holon wisdom query` accurately retrieves and ranks relevant entries from both local and global stores.
- [ ] `holon intent` detects existing related intents in local and global ledgers.
- [ ] `holon plan` incorporates precedent plans and historical wisdom into plan generation.
- [ ] `holon execute` verifies planned code modifications against past regressions and bugs.
- [ ] `pr-reviewer` and `pr-review-resolver` consult local and global wisdom during review evaluation and fix synthesis.
- [ ] `holon calibrate` records newly synthesized insights into both `holon-knowledge/wisdom/` and `~/.holon/wisdom/`.
- [ ] Workflow documentation, skill instructions, and prompt templates reflect the mandatory dual-tier knowledge checks.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: the string `wisdom` appears nowhere in
`apps/holon-coherence/src/` or `apps/sandbox-executor/src/`; no ledger/KB pre-action check is wired into intent, plan,
execute, review or calibration.

> [!NOTE] **Split out: Bean 0052.** This bean asks for consultation at _phase_ granularity. Bean 0052 specifies the
> _action_-level machinery underneath it -- multi-label fast retrieval, the per-action consult/verdict ledger with
> `unknown` handling, and the evidence-weighted rules that decide what becomes a veto versus a KB fact or wisdom rule.
> That machinery is what makes the five phase checks below implementable, so treat 0052 as the prerequisite and this
> bean as its consumer. Phase-level wording here stays as the requirement statement.
