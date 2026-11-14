# Engineering Rules

Benchmark data, token conservation, target repository isolation, test execution, the three-ledger invariant and file
sizing. Moved verbatim from `AGENTS.md`.

---

10. **Zero Synthetic Data for Benchmarking**: Absolutely never use synthetic or mock data to measure efficacy or
    benchmark token reduction. Official evaluations and scorecards must derive exclusively from authentic real data
    streams (live sandbox task executions, genuine wire logs, or real production payloads).
11. **Token Conservation & Concise Communication**: Minimise prompt and generation token burn across harness and
    subagents. Deliver dense, factual, and strictly actionable updates without narrative bloat. Intermediate review
    iterations stay local in `.subagent/` — never post premature review comments to GitHub until all findings are fully
    resolved or consensus approved. Prune stale `.subagent/` artifacts upon completion.
12. **Target Repository Isolation & Zero Harness Path Leaks**: Target repositories (`holon-agentic-coder` and
    `holon-coherence`) are independent, standalone software systems. They **MUST NEVER** know about, import, reference,
    or configure harness-specific directories, conventions, or tooling (`.beans/`, `todo/`, `.agents/`). Any path lists,
    ignore patterns, filters, or calibration logic inside target repositories must strictly contain target-native paths
    only (`holon-knowledge/`, `plans/`, `.holon/`). Harness concerns must never leak into target codebases.
13. **Strict Test Execution & Tooling Prohibition (NEVER `unittest`, NEVER `python3 -m unittest`, NEVER `PYTHONPATH`)**:
    All test suites across all target repositories and the harness MUST be executed strictly using `uv run pytest`.
    - Running `unittest`, `python3 -m unittest`, `python -m unittest`, or bare `pytest` is strictly forbidden.
    - Executing commands with `PYTHONPATH` overrides (e.g., `PYTHONPATH=...`, `export PYTHONPATH=...`) is strictly
      forbidden. All virtual environment dependencies and editable workspace packages are managed and resolved cleanly
      by `uv`; manual `PYTHONPATH` overrides mask packaging and dependency errors, bypass workspace definitions, and
      break hermetic testing.
14. **Canonical 3-Ledger Architecture Invariant (`holon-knowledge/ledger/`)**: Target repositories maintain strictly
    three append-only ledgers under `holon-knowledge/ledger/`: `intents.jsonl` (Intent), `plans.jsonl` (Plan), and
    `executions.jsonl` (Execution, Review, and Calibration). **NEVER create auxiliary ledgers like `actions.jsonl` or
    `reviews.jsonl`**. All discrete micro-action records (`entry_type: "action"`, such as `ACT-REV`, `ACT-FIND`,
    `ACT-POST`, tool operations) and lifecycle summaries (`entry_type: "summary"`, such as `E-...`, `REV-...`) MUST be
    interleaved chronologically inside `executions.jsonl` under `LedgerLock`. Auxiliary ledgers fragment the provenance
    trail, break downstream query engines, and are strictly prohibited.
    - **Ledger-Only Conflict Resolution (No Tests Required)**: When syncing or merging `origin/main` into a flow branch
      results in conflicts strictly confined to ledger files (`holon-knowledge/ledger/*.jsonl`), **do NOT run the test
      suites**. Simply interleave or append the JSONL records chronologically by their `created_at` timestamp, verify
      that all lines parse cleanly as valid JSON, commit the resolved merge, and push.
    - **Mandatory Target-Branch Conflict Resolution Before Review & Calibration**: Prior to posting an approved
      consensus review to GitHub or executing Stage 5 calibration, agents and loop orchestrators **MUST** verify that
      the PR is clean and mergeable against the target branch (`gh pr view <pr> --json mergeable,mergeStateStatus`). If
      `mergeable == "CONFLICTING"` or `mergeStateStatus == "DIRTY"` (which frequently occurs when concurrent PRs merge
      new entries into `holon-knowledge/ledger/`), the agent **MUST immediately fetch `origin/main`, merge `origin/main`
      into the PR execution branch, resolve the conflicts (interleaving ledger entries chronologically), commit, and
      push to origin**. Never post an approved review, never calibrate, and never report a PR as ready to merge while it
      is in a conflicting state against the target branch.
15. **Modular File Sizing & 200-Line Sizing Guideline**: Source files exceeding **200 lines** should generally be
    decomposed into modular packages and focused single-responsibility modules (e.g. `flow/`, `cli/commands/`, `proxy/`,
    `executor/`, `calibration/`). This is a recommended guideline and best practice rather than a rigid hard rule,
    intended to minimise cross-agent merge conflicts, serialization bottlenecks, and bloated review passes. Keep
    functions focused and prefer splitting collaborators, handlers, dispatchers, options, and models into dedicated
    files where sensible.

---
