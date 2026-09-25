---
# holon-agentic-coder-ref-metadata-0052
title:
  "Consult and record the ledger/KB/wisdom for every agent action: multi-label fast lookup, outcome logging,
  evidence-weighted promotion"
status: todo
type: feature
priority: high
tags:
  - holon-flow
  - knowledge-base
  - wisdom
  - ledger
  - continuous-learning
  - observability
  - intent
  - planning
  - execution
  - pr-review-loop
  - calibration
created_at: 2026-09-26T14:12:35Z
updated_at: 2026-09-26T14:12:35Z
---

Every **action** an agent takes -- not every phase, every _action_ -- must first consult the ledger, knowledge base and
wisdom base, and must then log its own outcome back into the ledger. Consultation has to be **fast enough to sit inside
the inner loop** (sub-10 ms, a few hundred injected tokens), retrieval is keyed on **multiple labels per action** (an
action is tagged `architecture` _and_ `security` _and_ `docker-networking` _and_ `uv-venv`, never one taxonomy), and the
recorded outcomes have to survive the fact that **failure is cheap to prove and success is not**.

Bean 0046 asked for the same consultation at _phase_ granularity and is still open. This bean is the action-level
machine underneath it: the read gate, the write path, the outcome state machine, and the promotion rules that decide
what becomes a veto, a KB fact, or a wisdom rule. 0046 becomes a consumer of this.

## Current state (audited 2026-09-26 against `holon-agentic-coder` @ `c80ce35`)

| Area                     | What exists today                                                                                                                                                                                          | Why it blocks the ask                                                                                                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Knowledge layout         | `holon-knowledge/ledger/{intents,plans,executions}.jsonl`; scaffold creates `holon-knowledge/{plans,kb}/` with `.gitkeep` only (`scaffold.py:364`)                                                         | `kb/` is always empty and `wisdom/` is never created. `wisdom` appears in **zero** source files in `apps/sandbox-executor/src/`.                                                        |
| Ledger writers           | Five independent append sites: `flow.py:357` (intents), `flow.py:489` (plans), `flow.py:634` (executions), `entrypoint/planner.py:364`, `entrypoint/intent_creator.py:73`                                  | No shared schema, no shared writer, no index. Every writer de-duplicates by reading the **whole file** then appending.                                                                  |
| Outcome vocabulary       | `intents.jsonl`: 13 × `proposed`; `plans.jsonl`: 13 × `proposed`; `executions.jsonl`: 12 × `success` / `failed`                                                                                            | One terminal verdict per record. There is **no** `unknown`, no late revision, no partial outcome.                                                                                       |
| How "success" is decided | `flow.py:610` -- `test_pass_rate = 1.0 if exit_code == 0 else 0.0`, i.e. one test-suite exit code                                                                                                          | A single binary signal is recorded as `success` and never revisited, so n=1 "proofs" already dominate the ledger.                                                                       |
| Action granularity       | The agent is one opaque subprocess: `build_cmd(model_name, prompt_file, intent_file, full_prompt)` (`agent_runner.py:326/382`) → `subprocess.run(..., capture_output=True)` (`entrypoint/executor.py:154`) | The inner loops (agent tool calls, repair iterations, review iterations) are **invisible**, so they cannot be consulted for or recorded.                                                |
| Static "wisdom" today    | `holon-config/world/ruleset.md` + `constraints.md`, hand-written, injected into planner/executor prompts ("All planning and execution agents must consult and obey these rules")                           | The only prescriptive knowledge in the system is **never updated by the loop**. Nothing the loop learns reaches it.                                                                     |
| Reusable substrates      | `OpenBrainMemory` (SQLite `~/.holon/openbrain/openbrain.db`, topic/category/content/metadata_json) and `RAGCodebaseIndexer` (AST symbols + keyword index)                                                  | Both are exported in `token_reduction/__init__.py` and **never instantiated**. The RAG indexer also rebuilds by walking the whole tree on every construction -- unusable inside a loop. |
| Calibration              | `calibration.py` computes predicted-vs-actual deltas, writes `plans/P-*_calibration.md` and stops                                                                                                          | Deltas are the cheapest success/failure evidence in the system and currently end up in a Markdown file nobody queries.                                                                  |
| CLI                      | `holon intent/plan/execute/calibrate/flow`                                                                                                                                                                 | No `consult`, no `record`, no `reconcile`, no `veto`, no `promote`.                                                                                                                     |

## What "every action" means (enumerated sites to instrument)

1. **Intent** -- intent creation, duplicate/overlap detection, EV and entropy gating, `REJECT`/`DEFER` decisions
   (`entrypoint/intent_creator.py`).
2. **Plan** -- decomposition into sub-intents, step ordering, agent/model choice, EV/entropy gate, world-ruleset
   compliance check (`entrypoint/planner.py`, `flow.py` plan stage).
3. **Execution loops inside the execution stage** -- each agent tool call (edit / bash / read / test), each repair
   iteration after a failing command, the verification test-suite run itself (`entrypoint/executor.py`,
   `agent_runner.py`).
4. **Loops inside the PR review loop** -- each reviewer-lane verdict, each resolver fix attempt per review comment, each
   push/rebase, each loop iteration (`.agents/skills/pr_reviewer`, `pr_review_resolver`, `pr_review_loop`).
5. **Calibration** -- each metric-delta judgement, each proposed tuning of EV/entropy physics (`calibration.py`,
   `holon-config/metrics/*.json`).

Each site emits a **pair**: a `consult` (pre-action question + what came back) and a `verdict` (post-action outcome).
The consult record is what lets us later prove the agent was warned; the verdict record is what makes the warning
sharper next time.

## Design requirement 1: multi-label, not a single taxonomy

A record carries a **set** of labels. Two kinds, both multi-valued, both indexed as one inverted index:

- **Curated concern labels** (small, reviewable vocabulary, ~30-80 entries): `architecture`, `security`, `testing`,
  `ci-cd`, `sandbox-networking`, `prompting`, `token-economy`, `git-worktree`, `dependency-management`, ...
- **Program-level labels** (open vocabulary, machine-derived, zero LLM cost): tool name (`tool:edit`, `tool:bash`),
  command signature (`cmd:uv-run-pytest`), file paths and AST symbols (`path:apps/sandbox-executor/src/...`,
  `sym:plan_local_llm_route`), environment facets (`env:docker-desktop`, `os:macos`), harness (`agent:agy`).

Rules:

- **No hierarchy, no exclusivity.** Facets (`concern`, `tool`, `subject`, `env`) exist only to group labels for display
  and query; an action may carry any number of labels from any number of facets at once. Adding `security` must never
  imply anything about `architecture`.
- **Query algebra**: `--all a,b --any c,d --not e` (conjunction / disjunction / negation) plus free text over content,
  resolved from the inverted index without touching the JSONL files.
- **Deterministic labels are free**: derived from tool, command, path and symbol at record time. LLM-proposed semantic
  labels are optional, capped (≤ 5), **cached by action signature** so the same action never pays for labelling twice,
  and never gate the veto path (a veto must be reproducible from deterministic labels alone).
- **Anti-sprawl**: canonical alias map (`mitm-proxy` → `mitmproxy`, `uv-venv` → `uv`), min-support merge sweeps,
  deprecated-label tombstones with redirect, and a hard cap on auto-applied labels per record. Label cardinality is a
  tracked metric; unbounded growth is a defect.

## Design requirement 2: consultation must be really quick

- **Budget**: p50 ≤ 5 ms, p95 ≤ 15 ms in-process; ≤ 50 ms cold start. Measured in CI, not asserted.
- **Prebuilt durable index**, never rebuilt per query: SQLite (FTS5 for text + an inverted `label → record id` table +
  an `action_signature` table) under `holon-knowledge/.index/` for the project tier and `~/.holon/index/` for the global
  tier. Incrementally updated by watching ledger mtime + byte offset, so appending one line costs one index insert.
- **Do not** reuse `RAGCodebaseIndexer` on the hot path in its current form (it walks the whole tree in `__init__`).
  Either reuse it with a persisted symbol map, or keep it for plan-time context only.
- **Bounded payload**: the injected block is capped (default top-k ≤ 6, ≤ 1.2k tokens, each rule one line plus its
  record id and posterior) and de-duplicated per session -- an action that consults twice in a loop must not pay twice.
- **Graceful degradation**: index missing, stale, or over budget ⇒ consult returns `unknown` + a diagnostic, and the
  action proceeds. Retrieval failure must never become a build failure.

## Design requirement 3: outcome logging, including outcomes that are not known yet

Append-only `holon-knowledge/ledger/actions.jsonl` (one line per action) with verdicts as **events**, so nothing is ever
rewritten. Verdict vocabulary:

| Verdict        | Meaning                                                            | Typical latency       |
| -------------- | ------------------------------------------------------------------ | --------------------- |
| `attempted`    | action started, consulted with record ids listed                   | immediate             |
| `success`      | objective post-condition held                                      | immediate or deferred |
| `failure`      | objective post-condition did not hold                              | immediate or deferred |
| `unknown`      | completed, but no post-condition observed yet                      | open                  |
| `inconclusive` | environment noise (flake, timeout, container loss) -- not evidence | immediate             |
| `abandoned`    | agent withdrew the action before a result                          | immediate             |
| `superseded`   | a later record replaces this action's context                      | immediate             |

Resolution sources, in order of authority: deterministic post-condition (exit code, `git ls-remote` ack, PR state, CI
run result) → human statement → model self-report (**never** sufficient for promotion, only for `unknown`).

Deferred and never-known outcomes are first-class:

- `holon reconcile` attaches late verdicts by ref (PR number, branch, CI run id, session id) and is cheap enough to run
  at the start of every flow stage as well as by hand.
- `unknown` records **expire** into `unresolved` after a TTL (default 14 days): they stay in the ledger forever but stop
  counting toward any posterior and can never contribute to a veto. The alternative -- letting "we never checked" rot
  into "we never do that" -- is the failure mode this design must avoid.
- Redaction before recording reuses the existing `redact_args` / `redact_text` machinery (`entrypoint/executor.py:102`),
  because action signatures contain commands and paths.

## Design requirement 4: failure is easy to prove, success is not

The two directions are not symmetric and must not share a policy.

**Failure → veto.** Deterministic, small-N, and dangerous when over-generalised:

- Promotion ladder `observed → repeated → contested → proven-fail`. `proven-fail` (the only state that can veto)
  requires: same `action_signature`, same **context fingerprint** (image digest, model + version, harness version,
  OS/arch, key dependency versions), ≥ 2 reproductions, zero successes, and a deterministic (non-flaky) failure class.
- A veto means: the consult response carries `veto: [...]`, the agent **must not** take that action and must either
  choose a documented alternative or stop and report the blocker. Veto enforcement is off by default and enabled per
  stage after shadow-mode measurement (below).
- **Vetoes decay.** Any context-fingerprint change, an explicit expiry (default 90 days), or a single contrary
  observation demotes to `contested`, lifts the veto, and appends the audit trail. Stale vetoes are worse than no
  vetoes: they silently shrink the search space of a system that is supposed to explore low-probability actions.
- Single flaky failures, `inconclusive`, and `unresolved` are excluded from vetoes by construction.

**Success → evidence.** A success is a statistical claim, so it is stored as one:

- Each `action_signature` keeps a Beta(α,β) posterior (Wilson 95 % interval surfaced alongside) updated by **every**
  natural re-run. Ladder: `observed` (n ≥ 1) → `repeated` (n ≥ 5) → `likely-success` (n ≥ 20 and Wilson lower bound ≥
  0.75) → `proven-success` (n ≥ 50 and Wilson lower bound ≥ 0.90, across ≥ 2 distinct context fingerprints).
- Advisory language is graded to the state, and **no success state ever produces a veto or a "must"**. Only
  `proven-fail` is imperative; everything success-shaped is phrased "prefer / worked before (n=…, LB=…)".
- We do not manufacture thousands of trials. Evidence is harvested opportunistically: the loop already re-runs the same
  signatures (repair iterations, review iterations, CI re-runs, calibration across plans), and every one of those is a
  free trial. Where revalidation is genuinely cheap, idempotent and safe (`uv run pytest -m "not integration_test"`,
  image existence checks, `--dry-run` git ops), calibration may schedule it; anything expensive, destructive,
  network-writing or user-visible is never re-run for statistics.
- Success transfers worse than failure, so scope transfers differently: **vetoes require fingerprint equality**, while
  advisories may cross fingerprints but are then labelled `transferred` and capped in authority.

**Both directions land in KB and WB, as different objects:**

- **KB (descriptive)**: what is true here -- facts, file/symbol maps, confirmed constraints, interface shapes, "endpoint
  X speaks protocol Y". Indexed by labels + subjects, TTL'd, never imperative.
- **WB (prescriptive)**: one record per rule -- `when <labels/conditions> do|never <action>`, posterior, trial counts,
  `first_seen`/`last_seen`, context fingerprints, `source_record_ids` back to ledger lines, review state (`auto` /
  `human-confirmed`), revalidation date. Only `proven-fail` rules may be worded as prohibitions; only `proven-success`
  rules may be worded as defaults.

## Interfaces

- `holon consult --labels a,b [--all .. --any .. --not ..] --tool <t> --subject <path|sym> [--budget-tokens N]` → JSON:
  `{veto: [...], advisories: [...], proven_fail: [...], likely_success: [...], missing_evidence: [...], consulted_ids: [...]}`
- `holon record --action-id <id> --signature <sig> --labels a,b --verdict success|failure|unknown|inconclusive|abandoned [--ref pr:57|ci:run:123|branch:...] [--evidence <ref>]`
- `holon reconcile` / `holon promote --pending` / `holon promote --approve <id>` / `holon veto list|lift <id>`
- `holon stats [--since 7d]` → hit rate, veto count and precision, advisory adoption, p50/p95 consult latency, injected
  tokens per action, label cardinality.
- Prompt/skill integration: `holon-config/prompts/{planner,executor}.template.md`,
  `entrypoint/{intent_creator,planner,executor}.py`,
  `.agents/skills/{pr_reviewer,pr_review_resolver,pr_review_loop}/SKILL.md`. Every consulted record id must be **echoed
  by the agent in its output**, so consultation is provable rather than merely available.

## Enabling it: making the inner loops observable

Nothing can be recorded today because the loops are opaque (`capture_output=True`, one blob of stdout). Cheapest
authentic sources, in preferred order:

1. **Native structured output** -- parse the agent's own stream (`agy --output-format stream-json` /
   `--input-format stream-json`, verified available on this host's `agy`; Claude Code `--output-format stream-json`) to
   get per-tool-call events with exit status. This is the highest-fidelity option and needs no extra model spend.
2. **Coherence wire telemetry** -- one record per LLM request already produced by the token-reduce sidecar (custom
   `rel_wire_logs`), which gives timing, provider and token deltas per turn, i.e. the review/repair iteration boundary.
3. **Harness hooks** (Claude Code hooks / pi extensions) where available, as a fallback for actions with no wire event.

The action signature must be stable across runs (normalise whitespace, absolute paths, ports, ids) or the posteriors
never accumulate.

## Acceptance criteria

- [ ] One shared ledger module: all five current append sites migrated to it, no per-write whole-file scan, dedupe via
      the index, append-only, existing ledger files replay-compatible.
- [ ] `holon consult` answers a 4-label conjunctive query in ≤ 15 ms p95 on a warm index and ≤ 50 ms cold, asserted by a
      CI benchmark over a seeded ledger of ≥ 50k records (seeded fixture is a **test corpus**, never a benchmark claim).
- [ ] Multi-label round trip: one action carrying `architecture` + `security` + `cmd:uv-run-pytest` + `path:<x>` is
      retrievable by each label individually and by their conjunction; adding a label never removes it from another
      query.
- [ ] `holon record` writes `attempted` + verdict events; `holon reconcile` resolves a PR-merge verdict recorded days
      later; an `unknown` older than TTL becomes `unresolved` and is provably excluded from posteriors and vetoes.
- [ ] Veto path: a `proven-fail` (2 reproductions, same fingerprint) blocks the action in `holon execute` (after shadow
      mode) with an actionable message naming the record id and the alternative; a single contrary observation or a
      changed context fingerprint lifts it and appends the audit trail.
- [ ] Success path: a signature at n=3 renders as `observed`, at n=20/LB≥0.75 as `likely-success`, at n=50/LB≥0.90
      across two fingerprints as `proven-success`, and **none of these** ever emits imperative text or a veto
      (string-level tests).
- [ ] Promotion writes one WB record per rule with posterior, counts, source record ids and revalidation date, plus a KB
      fact; `holon promote --pending` reviewable by a human, nothing auto-promotes to imperative without
      `human-confirmed`.
- [ ] All five lifecycle stages consult before acting and echo consulted ids; the ids are verifiable against the ledger.
- [ ] Self-metrics visible via `holon stats`; shadow-mode report shows veto precision against real re-runs before
      enforcement is turned on anywhere.
- [ ] `uv run pytest -m "not integration_test"` green, `uv run ruff check .` / `ruff format --check .` clean; efficacy
      measured **only** on authentic loop data (repo rule 10 -- no synthetic benchmark claims).

## Notes

- Target repository: `apps/holon-agentic-coder/` --
  `apps/sandbox-executor/src/sandbox_executor/{cli,flow,calibration,agent_runner,scaffold}.py`,
  `entrypoint/{intent_creator,planner,executor}.py`, `holon-config/{prompts,world,metrics}/`, `holon-knowledge/`, tests
  under `apps/sandbox-executor/tests/`. PR review loop integration also touches
  `.agents/skills/pr_review*`/`pr_review_loop` in this control plane.
- Relationship: **consumes** nothing from 0046 and is **consumed by** 0046; independent of Bean 0051 (harness endpoint
  work) and orthogonal to Beans 0038/0039/0040 (calibration + flow), which supply its best evidence stream.
- Invariants: ledgers stay append-only (never rewrite history -- same discipline as the `I-`/`P-`/`E-` provenance
  branches); local tier is the default and the global tier (`~/.holon/`) is opt-in, because a cross-repo veto is a
  foot-gun; no secret may enter a label, signature or subject; retrieval failure degrades to `unknown`, never to a
  block.
- Rollout: shadow mode everywhere → enforce vetoes in `execute` only → review loop → plan → intent. Enforcement is
  per-stage config, default off, and every enforcement flip needs a veto-precision number attached.
- Explicit non-goals: embedding-model semantic search (labels + FTS5 first; measure, then decide), automatic
  human-in-the-loop bypass, and any change to how PRs are merged (always human-only, Bean 0034).

## Resolution

Not yet started.
