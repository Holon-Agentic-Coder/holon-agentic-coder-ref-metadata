---
# holon-agentic-coder-ref-metadata-0097
title:
  "Fix and verify holon-coherence telemetry metrics (prefill speed 0, decode throughput distortion, and timing
  calculations)"
status: completed
type: bug
priority: high
tags:
  - metrics
  - telemetry
  - throughput
  - mitmproxy
  - timing
  - holon-coherence
created_at: 2026-10-15T22:35:00Z
updated_at: 2026-10-16T01:11:55Z
---

## Summary

Investigate, correct, and rigorously verify all telemetry metrics in `holon-coherence`:

1. **Prompt (Prefill) Speed Reporting 0.00 tokens/sec**:
   - Investigate why live metrics reported via `holon-coherence metrics` and `/holon/api/metrics` persistently show
     `0.00 tokens/sec` despite large prompt volumes (>1.2M tokens).
   - Audit `prefill_tps` calculation (`input_tokens / ttft`):
     - Ensure `ttft` is always accurately captured and non-zero across all endpoints (Anthropic, Gemini, OpenAI).
     - Guard against cases where `flow.request_start_time` or `flow.response_headers_time` is missing or set to `now`
       (causing `ttft = 0.0`).
     - Fix `_read_offline_metrics` in `src/holon_coherence/commands/metrics.py` and `CumulativeMetrics` in
       `src/holon_coherence/mitm_addon.py` so prefill throughput is faithfully aggregated.

2. **Decode Throughput Distortion (34,000–38,000+ tokens/sec)**:
   - Current calculation `output_tps = output_tokens / (total_time - ttft)` results in astronomical, unrealistic speeds
     (e.g. `34816.13 tokens/sec`).
   - Root causes:
     - **Non-streaming requests**: When responses are not streamed, headers and the complete payload arrive in the same
       network chunk or within 1–2 milliseconds of each other. `generation_time = total_time - ttft` collapses to socket
       parse time (~0.001s). Dividing output tokens by 0.001s yields >35,000 tokens/sec. Decode throughput is physically
       meaningless for non-streaming requests and must not be computed from `total_time - ttft`.
     - **Streaming requests**: Ensure mitmproxy response streaming (`flow.response.stream`) does not buffer chunks into
       a single burst before dispatching to the client. Ensure `first_chunk_time` reflects the actual first token chunk
       from upstream, and `generation_time` reflects genuine token streaming duration.
     - Add defensive thresholding: If `generation_time < 0.05` seconds or request is non-streaming, flag decode
       throughput as non-streaming/unmeasured rather than corrupting the average decode throughput metric.

3. **Comprehensive Metric Audit & Verification**:
   - Verify that all optimization and telemetry metrics are calculated correctly and consistently between the live
     in-memory proxy (`/holon/api/metrics`), the web dashboard (`/holon/`), and offline wire logs
     (`_read_offline_metrics`):
     - `total_input_tokens`, `total_output_tokens`, `total_cache_read_tokens`, `total_cache_creation_tokens`,
       `total_reasoning_tokens`.
     - `provider_cache_hit_rate` (`cache_read_tokens / total_input_tokens`).
     - `cache_hit_rate` (`cache_hits / total_requests`).
     - `tool_calls_pruned` (`tool_outputs_omitted`).
     - `tokens_reduced` and `chars_saved`.
     - `avg_ttft_ms` (`sum_ttft_ms / count_ttft`).
     - `avg_prefill_throughput_tps` and `latest_prefill_tps`.
     - `avg_tail_prefill_tps` and `latest_tail_prefill_tps`.
     - `avg_decode_throughput_tps` and `latest_decode_throughput_tps`.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)
- Target Files:
  - `src/holon_coherence/mitm_addon.py`
  - `src/holon_coherence/commands/metrics.py`
  - `tests/test_mitm_addon.py`
  - `tests/test_cli.py`

## Acceptance Criteria

- [ ] Non-streaming requests do not compute or corrupt `decode_throughput_tps`; decode throughput is exclusively
      computed from genuine streaming (SSE) chunk intervals.
- [ ] If streaming generation duration is below a realistic threshold (< 50ms), throughput calculations are guarded
      against division by near-zero duration.
- [ ] Prompt prefill throughput (`prefill_tps`) accurately computes and displays prompt tokens divided by TTFT (in
      seconds) whenever prompt tokens > 0 and TTFT > 0.
- [ ] All metrics in `CumulativeMetrics`, `/holon/api/metrics`, terminal output (`holon-coherence metrics`), and offline
      log parser are audited, mathematically verified, and consistent.
- [ ] Comprehensive test suite added in `tests/test_mitm_addon.py` and `tests/test_cli.py` asserting accurate prefill
      and decode TPS across both streaming and non-streaming responses.

## Resolution Summary

All five stages of the Holon flow have executed and **PR #19 is merged**: `holon-coherence` merge commit `97cc295` on
`main`, merged by the human maintainer at `2026-10-16T01:04:45Z`. The agent never merged anything — merging stayed on
the human side of the boundary exactly as `AGENTS.md` requires.

1. **Stage 1 (Intent)** — `I-1792075530-coherence-telemetry-metrics-prefill-decode/_`, row in
   `holon-knowledge/ledger/intents.jsonl`.
2. **Stage 2 (Plan)** — `.../P-1792075714-pi-agent-JANGQ-AI_Qwen3.8-Flash-Next-JANG_4M/_`, plan document in `plans/`,
   row in `plans.jsonl` (predicted EV 68.9).
3. **Stage 3 (Execute)** — `.../E-1792077739-pi-agent-JANGQ-AI_Qwen3.8-Flash-Next-JANG_4M/_`, row in `executions.jsonl`;
   implementation commit `fa77bd9`.
4. **Stage 4 (PR review loop)** — PR https://github.com/Holon-Agentic-Coder/holon-coherence/pull/19. Three iterations of
   the `pr-review-loop` skill on a local `vmlx` runtime (ensemble dispatched serially, three fresh blind contexts). 9
   findings dispositioned: 7 applied (`NIT-1`/`NIT-3` in `7ca3476`, `NIT-4`/`NIT-5`/`NIT-6` in `d15e385`,
   `NIT-8`/`NIT-9` in `c1b9c9f`) and 2 rejected with recorded evidence (`NIT-2` cache-hit header block — untouched by
   the diff, no `record_response` on that path; `NIT-7` legacy wire-log window — accepted by plan §5). Convergence at
   `c1b9c9f`: 3/3 `APPROVED`, 0 Critical / 0 Important / 0 open Nit, CI 7/7. Posted as a `COMMENT` review (id
   `5541688607`) because GitHub rejects `--approve` from the PR author.
5. **Stage 5 (Calibration)** — `holon calibrate <E-.../_>` produced
   `plans/P-1792075714-pi-agent-JANGQ-AI_Qwen3.8-Flash-Next-JANG_4M_calibration.md` (commit `2a52f49`): predicted EV
   68.90 → actual EV 77.44 (ΔEV +8.54, conservative underestimate), P(success) 0.90 → 1.00, cost 4.00 → 3.40, impact and
   learning value exact. The `/calibrated` ref was pushed, and the commit was fast-forwarded into the PR head branch
   (`c1b9c9f..2a52f49`) so the report is in the PR diff. CI 7/7 on `2a52f49`, `MERGEABLE`, then merged as `97cc295`.

No force-push and no rewrite of any audited `I-`/`P-`/`E-` ref; the four `I-1792075530-…` refs and the
`fix-0097-coherence-telemetry-metrics-prefill-decode` worktree are now cleanup-eligible, pending operator confirmation.
See **Progress (2026-10-15)** for the offline stages 1-3 replication and **Progress (2026-10-16)** for stages 4-5.

## Progress (2026-10-16) — stages 4 and 5 unblocked

The egress blocker cleared (`api.github.com` reachable, `gh` authenticated), so the runbook
`todo/runbook-0097-resume-flow-after-network.md` was executed as written, with two deviations worth recording:

- **Reviewer children must be write-capable.** The first reviewer-1 cast ran on the `reviewer` agent, which has no file
  write tool: it returned a verdict but left no report file, so the vote was discarded (a vote with no artifact cannot
  be audited) and re-cast on a write-capable child under explicit read-only guardrails. Reviewer 3 of iteration 1 also
  mis-typed `important=1` in its final message while its on-disk trailer said `IMPORTANT: 0`; the file was treated as
  the record.
- **Prettier config discovery is wrong inside a nested worktree.** This worktree lives inside the harness checkout, so
  prettier resolves the harness `.prettierrc.json` (printWidth 100, proseWrap always), which `holon-coherence` does not
  carry. Resolutions were formatted with `--no-config` on the changed files only; a repo-wide `prettier --write` here
  would reflow unrelated documents.

Loop artifacts: `.subagent/holon-coherence_pr19_state.json` (resume), `_coordination.json` (adjudication ledger),
`_loop_history.md`, three iteration-3 reviewer reports, `_consensus_review_iter_3_c1b9c9f.md`, `_posted_review.md`.

## Progress (2026-10-15)

**Blocked, then replicated offline.** The flow could not run end to end: the host has no network egress
(`api.github.com` times out, `git ls-remote` fails, `npx prettier` unreachable) and the `gh` keyring token is invalid.
The containerized planner/executor roles `git clone` the target repository from `origin` inside the sandbox, so stages
2-3 could not run that way either. At explicit user instruction the stage 1-3 artifacts were therefore produced locally
instead — the intent/plan/execute branch chain and the three ledger rows were written by the real
`sandbox_executor.flow` stage code (`run_intent_stage`, `run_plan_stage`) plus the canonical executor ledger row, while
the plan document and the code change were authored by the host pi session (`pi-agent`, local `vmlx`
`JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M`). This is the AGENTS.md "explicit user instruction" exception and is named in both
the code commit message and the plan document (§6).

- Worktree: `apps/holon-coherence/fix-0097-coherence-telemetry-metrics-prefill-decode`
- Intent branch: `I-1792075530-coherence-telemetry-metrics-prefill-decode/_` (`intents.jsonl` row)
- Plan branch: `.../P-1792075714-pi-agent-JANGQ-AI_Qwen3.8-Flash-Next-JANG_4M/_` with the full specification in `plans/`
  and `plans.jsonl` (EV 68.9)
- Execution branch: `.../E-1792077739-pi-agent-JANGQ-AI_Qwen3.8-Flash-Next-JANG_4M/_` with `executions.jsonl` (588
  tests, exit 0) and the implementation commit `fa77bd9`
- Resume checkpoint: `.holon/flow/checkpoint-coherence-telemetry-metrics-prefill-decode.json` (`current_stage: review`,
  `completed_stages: [intent, plan, execute]`)
- Nothing pushed. Runbook for pushing, PR creation, the review loop and pre-merge calibration:
  `todo/runbook-0097-resume-flow-after-network.md`

### Implementation

1. **Prefill `0.00 tokens/sec`**: `MitmproxyAddon.response()` back-filled a missing `flow.request_start_time` with
   `time.perf_counter()`, so `ttft == 0.0` and `input_tokens / ttft` degraded to a fabricated `0.0` reading next to
   1.2M+ prompt tokens. New `resolve_flow_timing()` keeps one clock domain, falls back to mitmproxy's epoch timestamps
   (`request.timestamp_start`, `response.timestamp_first_byte`/`timestamp_end`), and reports _unmeasured_ instead of
   `0.0` when nothing was observed.
2. **Decode 34k-38k tok/s**: `total_time - ttft` was used for every reply, but for non-streaming responses that window
   is socket parse time (~1-2 ms). Decode throughput is now computed only from the SSE chunk window
   (`last_chunk_time - first_chunk_time`, newly stamped in the `responseheaders()` wrapper), only for genuine streams,
   and only when the window is `>= 0.05 s`; otherwise it is `unmeasured` and never enters the cumulative average.
3. **Consistency**: new `src/holon_coherence/metrics_math.py` is the single arithmetic module used by
   `CumulativeMetrics`, `/holon/api/metrics`, the `/holon/` dashboard, the `holon-coherence metrics` scorecard and
   `_read_offline_metrics`. The wire log additively stores `streaming`, `generation_ms`, `prefill_tps`,
   `tail_prefill_tps`, `decode_tps`; `to_dict()` additively exposes `latest_decode_throughput_tps`, `latest_ttft_ms`,
   `latest_total_time_ms`, `decode_samples`. Legacy wire-log records without the flag are still admitted, but only
   through the same 50 ms floor.

### Acceptance criteria

- [x] Non-streaming requests do not compute or corrupt `decode_throughput_tps`
- [x] Generation windows `< 50 ms` are guarded against division by near-zero duration
- [x] `prefill_tps` computes prompt tokens / TTFT whenever both are positive
- [x] All metrics audited and consistent across proxy, API, dashboard, CLI and offline parser (equality test over 24
      shared keys)
- [x] Tests added in `tests/test_mitm_addon.py` (10) and `tests/test_cli.py` (5)
- [x] Stage 4 PR review loop consensus approval — 3/3 blind ensemble votes `APPROVED 0/0/0` at head `c1b9c9f`, posted to
      PR #19
- [x] Stage 5 calibration and inclusion of the report in the PR diff — `2a52f49` on the `/calibrated` ref and inside the
      PR diff

### Verification

`ruff check .` clean · `ruff format --check .` clean (72 files) · `pytest -m "not integration_test"` **588 passed** (3
port-dependent `start` tests deselected; they fail identically on the untouched base commit `6599f4b` because the local
proxy container occupies port 8080). `npx prettier` cannot reach the registry offline; the cached prettier 3.9.10 binary
was used instead and reports the markdown clean.
