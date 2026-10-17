# Local LLM Runtime Notes — `pr-review-loop`

Read this file **instead of improvising** whenever the orchestrating agent's own model is served locally. It collects
the rules that exist only because a local inference backend is shared by every child, plus the rules that exist because
the orchestrator's context window is finite and **will** compact mid-loop.

---

## 1. Detecting a local runtime

Classify the parent runtime **before the first fanout**, per
[coordination.md §4](../../coordination.md#4-dispatch-concurrency-local-vs-hosted-runtimes). It is local when any of
these hold:

- `$PI_PROVIDER` (or the harness's equivalent) is `vmlx`, `ollama`, `lmstudio`, `mlx`, `llama.cpp`, or similar.
- The model base URL is `localhost`, `127.0.0.1`, or a LAN host the operator's machine serves.
- The operator says the model runs locally, or has said it earlier in the session.
- A previous child in this session died with `reasoning_content but no visible answer and no tool call` — treat the
  runtime as local for the rest of the loop regardless of what the config says.

Record the classification in the loop's state file so a successor inherits it instead of re-guessing.

## 2. Dispatch rules (serial only)

- LLM-inference children run **one at a time**: launch, wait for termination, then launch the next. That includes the
  3-agent ensemble, the dry-run + resolver pair, and any parallel comment audit.
- **Serial is not singular.** Three distinct fresh child contexts, three distinct prompts, three independent blind
  votes, three report files, three trailer blocks. Never collapse the ensemble to one reviewer because dispatch is slow,
  and never pass an earlier vote into a later reviewer's prompt — that destroys the independence the ensemble exists to
  provide.
- The 3/3 unanimity requirement, the fresh-context rule, and the coordination ledger all stay exactly as written.
  Sequential latency is the accepted price of a run that completes.
- Never launch a replacement child next to a live sibling. A child that looks stuck is resumed or waited on, not
  duplicated: two children on one local backend is what made them stuck.

## 3. Compaction is expected. The cap is not your lever.

This harness compacts the orchestrator's context at a fixed window (currently **262k tokens**). A loop that runs several
iterations **will** compact, possibly several times. That is normal operation, not degradation, and it is explicitly
**not** a reason to do any of the following:

- **Do not reduce `max_iterations`.** The cap is the operator's cost governor (default 25) and never the orchestrator's
  comfort governor. Never invent a smaller cap, and never report a self-imposed one as "the cap is exhausted".
- **Do not stop early because context is filling up.** Compaction is survivable here by design: the loop's real state
  lives in files, not in the window — `.subagent/<repo>_pr<N>_state.json`, `.subagent/<repo>_pr<N>_coordination.json`,
  and one report file per reviewer.
- **Do not pause to ask whether to continue** an authorised loop. Half-asked pauses are the costliest habit in these
  runs. Continue, and report at the end.
- **Do not shorten the protocol to save tokens** — no merged reviewers, no skipped trailer blocks, no "I already know
  what reviewer 2 would say", no voting on a child's behalf.

After a compaction, rehydrate from files rather than from memory or from the operator:

```bash
jq -r '"head=\(.last_head // "?") iter=\(.current_iteration // "?") result=\(.last_result // "?")"' \
  .subagent/<repo>_pr<N>_state.json
jq -r 'keys_unsorted | join(", ")' .subagent/<repo>_pr<N>_coordination.json
ls .subagent/<repo>_pr<N>_*_iter_*.md
```

If the rehydrated state contradicts what you remember, **the files win**, and you say so rather than reconciling the
memory to the file.

### Keeping the window lean (so compaction costs less)

- Read reports with `grep`/`jq` excerpts targeted at verdicts and findings; do not re-read whole report files, whole
  diffs, or whole ledgers to refresh a fact you can extract in one command.
- Use the OS toolbelt (`jq`, `awk`, `grep`) for JSON and logs; do not write throwaway Python/Node to inspect data.
- Quote findings by their `file:line` and one-line summary in coordination notes; the report file holds the prose.
- Prefer running the numbers over re-deriving them in prose.

## 4. Shaping child prompts for a local backend

Long open-ended prompts are what time out locally. Every reviewer prompt gets:

- **A bounded command list** — the specific commands or read targets, in order, usually four to six, with "run nothing
  else" stated.
- **A hard time budget** stated in the prompt (e.g. "stop at 8 minutes whatever the state") matched by the dispatch
  timeout, which should be generous: 660000–1200000 ms, because a local child spends real time in inference.
- **A write-capable child agent type**: Every child dispatched for review, consensus, or resolution MUST have tool
  access to write files directly. In child harnesses (such as `pi`), do NOT dispatch to read-only agent roles like
  `reviewer` or `research` that lack a file-write tool; select an agent type that can write files (or equip it with
  write capabilities).
- **Admissible identifier discovery**: If the harness's admissible `agent` or `model` names are not documented or known
  upfront, probe the harness with an intentionally invalid identifier (e.g. `agent: "__probe__"`). The error returned by
  the child runner will list the permitted agent types and model identifiers without launching or burning resources.
- **A report-first discipline**: write to the report file after each step, so a timeout still leaves a readable partial
  artifact rather than an empty file.
- **A size ceiling** on the report (≤ 50 lines for a focused pass) and a trailer block verbatim, so the orchestrator can
  parse verdicts with `grep` instead of reading essays.
- **A stated "clean is a complete answer"**: `APPROVED` with zero findings is useful; do not invent findings.
- Read-only guardrails restated every time (no edits, no staging, no push, no merge, scratch only in `/tmp`, no writing
  state or coordination files).

## 5. Attrition handling

A timeout on a local runtime is an infrastructure event, not a review outcome.

- Read the report file first: a timed-out child that wrote its verdict is still a vote; one that left `NOT VERIFIED YET`
  placeholders is **not** a vote and must not be counted or described as a `CHANGES_REQUESTED`.
- **No file on disk = not a vote**: A child that completes or times out without leaving an on-disk report file (e.g.
  returned a trailer block in its chat message but could not write to disk) is **not a vote**. Its unpreserved findings
  cannot be acted upon or resolved. The pass is recorded `DEAD` in `passes[]` of `_state.json` and must be re-cast on a
  write-capable child.
- **On-disk report trailer beats child message**: If the child's final chat response contradicts its on-disk trailer
  block (e.g. chat claims `important=1` while the on-disk file says `IMPORTANT: 0`), **the file governs**. The on-disk
  artifact is the durable record of truth. Never silently reconcile the numbers; log the discrepancy in
  `<repo>_pr<N>_loop_history.md`.
- Recover with a **finish-only resume**: one child, an explicit list of the remaining commands, a short budget, and an
  instruction to fill the existing report file. Two failed finishes is the limit for a head; after that, record the
  reviewer as FAILED with the artifact path and re-cast the ensemble rather than grinding.
- A verdict written by a child whose checks are unverified is a placeholder, not evidence. Quote it as such.
- Never let attrition change the termination rule. Three votes at one head is the gate; two votes plus one failure is
  not approval, and it is stated as not-approved.

## 6. What local never licenses

Collapsing the ensemble · leaking votes between reviewers · reusing one reviewer's verdict across heads · treating an
earlier head's votes as counting toward the current head · approving on 2/3 · editing or amending an audited flow ref to
make convergence cheaper · posting "approved" when no head held three clean votes · quietly lowering the cap because the
run is long or the window is compacting.
