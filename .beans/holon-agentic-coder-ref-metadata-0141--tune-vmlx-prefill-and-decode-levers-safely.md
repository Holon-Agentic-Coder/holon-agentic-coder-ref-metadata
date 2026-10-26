---
# holon-agentic-coder-ref-metadata-0141
title: "Tune vmlx prefill and decode levers for both Qwen3.8 models, crash-safe"
status: todo
type: task
priority: normal
tags:
  - vmlx
  - local-llm
  - performance
  - prefill
  - decode
  - kv-cache
  - qwen3.8
created_at: 2026-10-22T14:29:12Z
updated_at: 2026-10-22T14:29:12Z
---

Tune the prompt-processing (prefill) and token-generation (decode) levers of the local vMLX stack for **both**
`JANGQ-AI/Qwen3.8-27B-JANG_4D` (port 8004) and `JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M` (port 8000), with a procedure that
stays correct if the vmlx engine or gateway is down, crashes mid-tweak, or is restarted by the OS at any point.

## Grounding (measured 2026-10-22 on the live host, M5 Max / 128 GB)

Current 27B backend launch line (from `ps`; the vMLX.app Electron process spawns each backend this way — the app owns
the launch arguments, `defaults read net.vmlx.app` holds only UI state):

```
vmlx_engine.cli serve <bundle> --host 127.0.0.1 --port 8004 --timeout 900 --max-num-seqs 1 \
  --prefill-batch-size 512 --prefill-step-size 2048 --completion-batch-size 512 \
  --is-mllm --no-continuous-batching --tool-call-parser xml_function --enable-auto-tool-choice \
  --reasoning-parser qwen3 --no-paged-cache --no-vision-memory-cache \
  --ssm-state-cache-size 0 --ssm-state-cache-mb 0 --disable-prefix-cache \
  --enable-block-disk-cache --block-disk-cache-max-percent 10 --stream-interval 8 \
  --speculative-model <bundle>/dflash2 --no-jit
```

Baseline (27B, last real request): prefill 166 tps uncached / 2,447 tps cached (dflash2-SSD hit, 18,693/20,023 prompt
tokens), TTFT 8.18 s (0.70 s of it SSD load of 117k cached tokens), decode 28.8 tps (draft 5, widths 5/8/16, acceptance
0.399), memory 23 GB active / 27.7 GB peak of 115.4 GB device limit. Flash-Next backend currently stopped; its launch
line must be captured from the app when first started (step 0).

Metrics source: gateway `:8081/health` (backend list) and each backend `:800x/health` (`last_request` with
prefill/decode tps, `ttft_s`, `cache_detail`, speculative stats, `effective_defaults`, memory, cache telemetry).

## Levers (all are vmlx-engine settings; none belong in pi or the weight bundle)

### Prefill / prompt processing

| Lever                                                     | Current                                                         | Tweak                                                                                                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| In-DRAM prefix cache                                      | `--disable-prefix-cache`                                        | Enable; hot prefixes then hit in RAM instead of SSD (SSD load added 0.70 s to TTFT). A/B against the SSD-only baseline.                       |
| SSD block-disk cache budget                               | `--block-disk-cache-max-percent 10` (~185.8 GiB observed)       | Raise if cross-session hit rate is low; this is the biggest single TTFT win for long agent sessions (166 tps recompute vs 2,447 tps SSD hit). |
| Prefill chunking                                          | `--prefill-batch-size 512 --prefill-step-size 2048`             | Try step 4096/8192 (fewer graph launches per 20k prompt); keep batch within memory headroom.                                                  |
| JIT                                                       | `--no-jit`                                                      | A/B removing it; compiled graphs typically pay back on repeated prefill shapes.                                                               |
| GDN decode kernels (decode-side, listed for completeness) | `VMLX_QWEN35_FUSED_GDN_CONV`, `VMLX_QWEN35_FUSED_GDN_GATES` off | Enable via env, A/B decode tps.                                                                                                               |

### KV cache

| Lever                     | Current                                                                                        | Tweak                                                                                                                                                                                           |
| ------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SSM companion-state cache | `--ssm-state-cache-size 0 --ssm-state-cache-mb 0` (`ssm_ram_enabled: false`)                   | Enable a bounded SSM RAM cache: hybrid-SSM models must re-derive SSM state on partial attention-KV hits; a bounded cache should cut re-prefill cost. Highest-risk lever (memory) — start small. |
| KV storage quantisation   | `attention_kv_storage_quantization` / turboquant disabled (engine-blocked by hybrid SSM state) | Investigate only; do not force. Track whether the engine gains per-attention-layer TQ KV for `qwen3_5` hybrid.                                                                                  |
| Paged cache               | `--no-paged-cache`                                                                             | Low priority under `--max-num-seqs 1`; revisit only if concurrency grows.                                                                                                                       |

### Decode / token generation

| Lever                               | Current                                                                                                                                                                | Tweak                                                                                                                                                                                 |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Speculative draft depth/width       | dflash2 draft, configured 5, runtime-selected widths 5/8/16, acceptance 0.399                                                                                          | Raise configured draft tokens (8/12) or bias the width schedule; acceptance must stay above ~0.5-of-draft for a net win (verify with `generation_tps`, not just `emitted_per_cycle`). |
| Stream interval                     | `--stream-interval 8`                                                                                                                                                  | Lower (e.g. 2–4) to cut perceived inter-token latency; no throughput effect.                                                                                                          |
| MTP (native multi-token prediction) | 27B: dropped in bundle (`bundle_has_mtp=false`). Flash-Next: **blocked** per the bundle's own `vmlx_mtp_tuning.json` (0.69× vs AR at every depth, measured 2026-08-27) | Do not re-enable; the shipped tuning file is the verdict.                                                                                                                             |
| `DFLASH_VERIFY_QMM`                 | off                                                                                                                                                                    | Only relevant if MTP were used; skip.                                                                                                                                                 |

### Both models, per-model notes

- 27B-JANG_4D: hybrid GDN/attention (48 linear + 16 full attention layers, GQA 24q/4kv), dflash2 draft in bundle, MTP
  dropped.
- Flash-Next-JANG_4M: MoE "Flash" family, ships `vmlx_mtp_tuning.json` + `vmlx_mtp_proposal_head.json` (MTP blocked;
  proposal head 4-bit, `acceptance_validated: false` — sha256-verify before any use, fall back to RTN on mismatch).
- Tune **one backend at a time** (they share the unified memory; `single_model_mode` today means the gateway serves one
  running backend).

## Crash-safe procedure (the plan must hold with vmlx down or dying)

Invariant: **every change is made to persisted configuration, never to live process state; applying a change always
means "restart one backend". A dead server is therefore never an unsafe state — it is just a state where the
already-staged config has not been applied yet.**

0. **Locate and snapshot the persisted per-model launch config** owned by vMLX.app (its settings store under
   `~/Library/Application Support/vmlx/` or equivalent; the `ps` line above is the ground-truth fallback). Snapshot it
   (dated copy) and record the full launch line per model. This step works with the server fully down and is a
   prerequisite for all others.
1. **Draft each tweak as an offline config diff** (file edit in the app's config store, or a documented UI action with
   before/after screenshots of the config). No running engine required.
2. **Apply one lever per restart.** Stop that one backend (app UI or engine pid), apply the single delta, start it.
   Never stack an unverified change on another.
3. **Gate before measuring:** backend `:800x/health` shows `model_loaded: true`, `effective_defaults` unchanged where
   not intended (`max_output_tokens` 16384, `max_prompt_tokens` 262144 — any drift means the tweak touched caps; stop,
   see Bean 0140), and memory has ≥ 20 % device-limit headroom after load. Then run the smoke request (step 5 fixture,
   small output) and confirm sane content.
4. **On any failure or crash: roll back the single delta from the snapshot, restart, confirm the gate, record the failed
   lever and symptom.** Config-on-disk + snapshot makes rollback independent of whether the server is alive. Treat an
   OOM-style crash as a rollback signal, not a retry case.
5. **Measure with real data only** (rule 10, no synthetic benchmarks):
   - Prefill fixture: a captured real ~20k-token agent-session prefix (harness system prompt + tools + genuine
     conversation, from real wire logs); record `ttft_s`, prefill tps, `cached_tokens`, `cache_detail`.
   - Decode fixture: a fixed real task prompt with a bounded `max_tokens` (e.g. 512, then 2048); record decode tps,
     draft acceptance, `generation_tps`.
   - Run the fixture cold (no cache), warm (same session re-prompt), and across a restart (SSD persistence check).
6. **Keep `--timeout 900` ≥ worst-case response**: worst case 16,384-token response is ≈ 9.5 min at current decode rate
   (Bean 0140 findings); any decode change that slows generation must re-check this bound.
7. **Record the outcome per model** in this bean: final launch line, before/after table per lever, keep/rollback
   decision. If any winning change alters effective output/context caps, sync `~/.pi/agent/models.json` (Bean 0140) and
   re-verify both sides.

## Acceptance criteria

- Both models have a final persisted launch config plus a measured before/after row per lever tried (TTFT, prefill tps
  cold/warm, decode tps, draft acceptance), kept or rolled back with reason.
- At least one rollback from snapshot was demonstrated with the backend stopped, proving the procedure is safe with the
  server down.
- No lever left half-applied; gate (step 3) passed on the final config for each model.
- `effective_defaults` caps unchanged (or explicitly changed and mirrored in pi, Bean 0140).
- All measurements from real request data; nothing synthetic.

## Notes

- This is host-infrastructure tuning on this Mac (vMLX.app + `~/.cache/vmlx-engine/`), not a change to
  `holon-agentic-coder` or `holon-coherence` source: the 5-stage Holon flow does not apply to the host server config
  itself. Any codification of the winning config into the harness (e.g. `local_llm.py` pre-flight checks, `holon doctor`
  output, launch recipes in harness docs) is harness/target work and routes through the flow or its own bean.
- Bean 0140 (output ceiling must be explicit — caps are cross-checkable via `:8081/health` + backend `/health`), Bean
  0138 (why single-response caps are fatal), Bean 0139 (turn budgets), Bean 0049 (why `local_llm.py` exists).
