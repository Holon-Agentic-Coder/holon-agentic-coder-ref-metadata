---
# holon-agentic-coder-ref-metadata-0142
title: "Extensive real-workload benchmark: Qwen3.8-27B-JANG_4D vs Qwen3.8-Flash-Next-JANG_4M for agentic coding"
status: todo
type: task
priority: high
tags:
  - benchmark
  - model-selection
  - vmlx
  - local-llm
  - qwen3.8
  - agentic-coding
  - performance
  - quality
created_at: 2026-10-22T15:10:00Z
updated_at: 2026-10-22T15:10:00Z
---

## Problem

The flow's local-runner model choice is currently a guess. Three beans (0132, 0129, 0133) are blocked waiting for a
usable agent runner, and `pi-agent` on the vMLX gateway is the only candidate that has ever started a flow stage on this
host. Two very different models are available, and the observed speed order contradicts the naive "bigger is better"
assumption:

- `JANGQ-AI/Qwen3.8-27B-JANG_4D` (`:8004`): **dense** 27B — 64 layers, hidden 5120, dense FFN (intermediate 17408),
  hybrid attention (16 full-attention of 64 layers, `full_attention_interval: 4`), GQA 24q/4kv, head_dim 256, **4-bit
  AWQ** (group 64). ~23.2 GB active / 54.4 GB peak. dflash2 speculative decode configured (draft 5 tokens, ~40 %
  acceptance, 28.8 tok/s measured).
- `JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M` (`:8000`): **MoE** — 48 layers, hidden 2560, **512 experts, 10 active per
  token** (moe_intermediate 640, ~2.5–3 B active params per token), hybrid attention (12 full-attention of 48 layers),
  GQA 24q/2kv, head_dim 256, **8-bit** group-64 quant. ~81.4 GB active / 85.1 GB peak.

Observed on 2026-10-22: the 27B dense model is **slower** than Flash-Next. The expected mechanism is active bytes per
token — decode on unified memory is bandwidth-bound, and the dense model reads ~13.5 GB of weights per token at 4-bit
while the MoE reads ~3 GB at 8-bit — but that is a hypothesis, not a measurement, and **speed is not the question the
benchmark exists to answer**. The question is which model is the better _agentic coding agent_: same-stage wall time,
cache economics, output quality, and failure behaviour on real work.

## Grounding (measured 2026-10-22, live host, M5 Max / 128 GB)

- 27B prefill: 3,555-token cold prompt 100.98 s (~35 tok/s, includes first-request warm-up); warm prefix-cache hit 0.29
  s (~12,356 tok/s). Findings from the 27B backend: prefill 166 tps uncached / 2,447 tps SSD-tier cached, decode 28.8
  tps with speculation.
- Both models are hybrid linear/full attention; only 1 in 4 layers carries full-attention KV, so per-token KV is small
  (~30 KB/token class) and the KV quantisation lever is off (hybrid SSM state) — cache capacity is not the
  differentiator, **RAM headroom is**: Flash-Next leaves ~21 GB for everything else, 27B leaves ~80 GB.
- Real workload sources exist in-repo (this is what the benchmark must consume — see Scope).

## Scope

### Zero synthetic data (hard constraint, AGENTS.md checklist item 10)

Every workload must come from an authentic real data stream — live sandbox task executions, genuine wire logs, or real
production payloads. No generated tasks, no SWE-bench-style synthetic instances, no mock repos, no canned prompts
written for the benchmark. The benchmark's own prompts are the flow's real stage templates rendered with real ledger
payloads.

### Workload set (real, stratified by size)

- **Plan stage — 5 workloads**: real merged intents reconstructed at their historical state: the intent JSON from
  `holon-knowledge/ledger/intents.jsonl` plus `planner.template.md` (167 lines) plus the repo checked out at the intent
  branch's base commit. Sample across sizes: a small single-bean fix (e.g. coherence PR #26), a multi-bean package (e.g.
  coherence PR #25), a large decoupling/audit task (e.g. AC PR #85), a docs task (AC PR #87), and a container/test task
  (AC PR #88).
- **Execute stage — 3 workloads**: real `E-...` branches from merged PRs at small / medium / large diff size, run from
  the plan-branch tip with the **real merged plan document** as input; ground truth is the real merged diff and the real
  post-merge test outcome.
- **Review stage — 2 workloads**: real PR diffs with known adjudicated findings — coherence PR #26 iteration-4 (NIT-6a
  wall-clock deadline, NIT-6b ledger gap) and AC PR #88 (4 lint/test findings) — scored for detection.
- **Intent stage — 2 workloads**: real intent JSONs with their question/answer sets.

`N = 3` runs per (model, workload), interleaved, to bound order and thermal effects.

### Protocol

- Drive both models through the **real containerised dispatch** (`holon plan` / `holon execute` / review-loop with
  `--agent pi-agent --model vmlx/<model>`, `HOLON_LOCAL_LLM=1`), not a raw API harness — the measurements must include
  the actual pipeline (this doubles as a dry-run of the Bean 0137/0138/0139/0140 fixes once they land).
- One backend resident at a time (`single_model_mode`); record RAM headroom and `vm.swapusage` before every block; a run
  whose backend dies is restarted, logged, and **excluded**, never silently retried.
- Pin the envelope: `maxTokens 16384` (declared in `~/.pi/agent/models.json`), gateway `effective_defaults` (temperature
  1.0 / top_p 0.95 / top_k 20) unchanged, reasoning mode `auto` as the primary condition with `low` (where honoured) as
  a secondary condition per Bean 0140.
- Cold measurements on a restarted backend (empty cache); warm measurements as the repeat of the same stable prefix.

### Metrics per run (all from real runs and wire logs)

- **Prefill**: cold tok/s, warm tok/s, TTFT, prefix-cache hit/miss, `memory.cache_mb`, SSD-tier vs RAM-tier hits.
- **Decode**: tok/s (speculation on/off where applicable), output tokens, thinking tokens (`reasoning_content`),
  `stopReason` distribution (`stop` / `length` / `error`).
- **Wall time**: per stage and per turn, turn count, tool-call count and JSON validity rate, stall/budget events (Bean
  0139 definitions), truncations.
- **Quality (the gate)**:
  - Plan: metrics-table parse rate, required sections present, EV arithmetic correct against the **real calibration
    reports** (merged `plans/P-*_calibration.md` give ground-truth predicted vs actual), structural similarity to the
    real merged plan.
  - Execute: `uv run pytest` pass on the real repo state, `ruff` clean, diff applicability, line-level F1/Jaccard
    against the **real merged diff**.
  - Review: precision/recall against the real adjudicated findings (NIT-6a/6b; the 4 PR #88 findings), false-positive
    rate.
- **Memory**: active/peak/cache GB and swap delta per block.
- **Economics**: tokens in/out, cache read/write, wall time per stage (local cost = wall time × power, or token counts —
  state the basis in the scorecard).

### Decision rules

- **Quality gate first**: speed is only compared between models that pass the floor — plan parse ≥ 90 % across runs,
  execute workloads passing the real test suite, no systematic tool-call breakage, review recall ≥ 1/2 on the known
  findings. A faster model that fails the floor is not eligible whatever its tok/s.
- Among eligible models: rank by stage wall time (weight plan and execute, where the flow spends its time), then cache
  economics, then memory headroom (swap behaviour counts as a first-class risk, not a footnote).
- Record a single recommendation — or a documented tie with the tie-breaker — and what would flip it (e.g. a RAM change,
  a new model on the gateway).

### Deliverables

- A scorecard in the harness `docs/` (harness artifact — it must not enter either target repository) where **every
  number is traceable to a run id and its wire log / session log**; scratch under `todo/` while working.
- All artifacts retained (rendered prompts, generated plans, produced diffs, wire logs) so the scorecard is auditable
  and re-scorable.
- The recommendation applied: the flow's default model updated (and Beans 0132 / 0129 / 0133's "runner" note corrected
  to name it), with the losing model retained as the fallback.

## Acceptance criteria

- Both models measured on every workload in the set, `N ≥ 3`, all numbers traceable to real runs — zero synthetic data.
- The quality gate is applied and recorded before any speed comparison is quoted.
- A documented model recommendation (or tie) exists, the flow default is updated to it, and the pending beans' runner
  notes reference it.
- No `main` worktree was used for benchmark runs; no PR was created or merged; all benchmark work lived in dedicated
  worktrees with their own virtualenvs.

## Relates to

Bean 0132 / 0129 / 0133 (waiting on a usable runner — this picks the model), Bean 0141 (the vmlx levers this benchmark
must hold constant or vary deliberately), Bean 0140 (the envelope the runs run under), Bean 0137 (runner selection),
Bean 0138 / 0139 (the failure modes the quality and wall-time metrics capture), and AGENTS.md checklist item 10 (the
zero-synthetic-data rule this whole design exists to satisfy).
