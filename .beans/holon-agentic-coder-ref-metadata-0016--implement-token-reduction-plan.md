---
id: holon-agentic-coder-ref-metadata-0016
title: Implement AI Agent Token Reduction Architecture & Action Plan
status: done
type: task
created_at: 2026-08-28T18:36:00+10:00
updated_at: 2026-08-28T18:37:00+10:00
---

# Implement AI Agent Token Reduction Architecture & Action Plan

## Context

Implemented `docs/optimisation/token_reduction_plan.md` in the reference repository inside dedicated Git worktree
`holon-agentic-coder-ref/feat-0016-token-reduction-plan` on branch `feat/0016-token-reduction-plan`.

## Resolution Summary

1. **Phase 1: MITM Interceptor & Certificate Trust Bootstrap**
   - Created `sandbox_executor.token_reduction.ca_generator` to generate self-signed Root CA certificates
     (`holon-root-ca.crt` & `holon-root-ca.key`).
   - Updated `sandbox_executor.cli` to mount CA certificates into container
     (`/usr/local/share/ca-certificates/holon-root-ca.crt`) and inject proxy environment variables (`HTTP_PROXY`,
     `HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`, `SSL_CERT_FILE`).
   - Implemented `sandbox_executor.token_reduction.mitm_addon` for MITM proxy request/response interception and
     short-circuiting.

2. **Phase 2: Context Cleaning & Prompt Cache Optimization**
   - Built `sandbox_executor.token_reduction.payload_cleaner` supporting Anthropic, OpenAI, and Gemini message payload
     formats.
   - Implemented tool output deduplication across conversation turns (replacing duplicate file reads in older history
     turns with `[Omitted: Content of resource is identical to Turn N]`).
   - Integrated automatic Anthropic prompt cache control insertion (`"cache_control": {"type": "ephemeral"}`).
   - Implemented conversation turn summarization when history exceeds threshold.

3. **Phase 3: Hybrid & Semantic Cache Layer**
   - Created `sandbox_executor.token_reduction.hybrid_cache` disk-backed SQLite store.
   - Built prefix tree key generator with normalization (stripping timestamps, task IDs, and UUIDs).
   - Implemented Jaccard/token-similarity semantic matching for prompts with minor text variations.

4. **Phase 4: RAG Codebase Indexing, OpenBrain Memory, & Ringer Orchestration**
   - Built `sandbox_executor.token_reduction.rag_indexer` with AST symbol extraction (`graph_find_symbol`) and keyword
     relevance search (`semantic_search`).
   - Built `sandbox_executor.token_reduction.openbrain_memory` for episodic cross-session memory retention.
   - Built `sandbox_executor.token_reduction.ringer_orchestrator` to delegate subtasks from Architect to fast Executor
     subagents and summarize execution output.

5. **Validation**
   - Added unit test suite `test_token_reduction.py`.
   - Verified 88 unit tests pass clean with 100% test pass rate.
   - Formatted all Python files with `ruff format .` and markdown files with `npx prettier`.
