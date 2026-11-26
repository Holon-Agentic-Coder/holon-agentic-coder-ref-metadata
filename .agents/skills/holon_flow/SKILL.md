---
name: holon-flow
description:
  Automates executing the full 5-stage Holon flow (intent -> plan -> execute -> review -> calibrate) inside an
  autonomous background subagent with automatic model fallback, checkpoint resumption, PR verification, and calibration
  inclusion. Activate this skill whenever the user asks to run holon flow, execute a bean through the flow, run a flow
  in the background, or invoke `/holon-flow`.
---

# Autonomous Holon Flow Driver Skill (`holon-flow`)

> [!NOTE] **Model tier: lowest.** This skill is mechanical, so run it in a dedicated subagent on the lowest-tier model,
> found by probing the harness as described in [`.agents/model-tiers.md`](../../model-tiers.md). Do not hard-code a
> model name here.

This skill orchestrates the end-to-end execution of the 5-stage Holon development lifecycle across target repositories
(`holon-agentic-coder` and `holon-coherence`). To avoid hijacking the user's primary interactive session for the
multi-hour containerised lifecycle, **the flow is executed inside a dedicated background subagent**.

---

## 📐 Architecture & Principles

1. **Background Subagent Execution (Bean 0212 & Flow Delegation)**: Running `holon flow` across all 5 stages takes
   between 15 minutes and several hours depending on plan complexity and review iterations. The main interactive agent
   **MUST NOT execute the flow inline**. Instead, it delegates to a background `Holon Flow Subagent` (`invoke_subagent`
   with `TypeName: "self"`, `Role: "bean <id> - holon flow <slug>"` (named per
   [subagents.md, "Subagent names"](../../subagents.md#subagent-names)), `Model` = the lowest tier per
   `.agents/model-tiers.md`) and immediately returns control to the user. Up to **4 concurrent `holon-flow` background
   subagents** may run at once on hosted runtimes (each in its own `flow-<slug>` worktree; local runtimes stay at 1),
   with automatic backfill of the next highest-priority ready bean once a PR merges per `post-pr-merge`.
2. **Sole Change Path Invariant**: Every target codebase change (`holon-agentic-coder` or `holon-coherence`) MUST
   traverse the 5 containerised stages:
   - **Stage 1 (Intent)**: `I-{ts}-{slug}/_` branch created and logged to `holon-knowledge/ledger/intents.jsonl`.
   - **Stage 2 (Plan)**: `P-{ts}-{agent}-{model}/_` branch, plan markdown (`plans/P-*.md`), EV estimation, logged to
     `plans.jsonl`.
   - **Stage 3 (Execute)**: `E-{ts}-{agent}-{model}/_` branch, implementation code, tests, logged to `executions.jsonl`.
   - **Stage 4 (Review Loop & Resolver)**: In-container review ensemble and native Stage 4 resolver converging on
     unanimous 3/3 consensus approval posted to the PR.
   - **Stage 5 (Calibration)**: `/calibrated` audit branch created, calibration report (`plans/P-*_calibration.md`)
     generated, and calibration commit fast-forwarded or merged into the PR branch so it is included in the PR diff.
3. **Canonical `holon flow` Runner**: Changes to target codebases MUST always be executed using the unified
   `holon flow <intent.json>` runner directly (or with `--from-stage` / `--checkpoint` when resuming). Never use ad-hoc
   wrapper scripts (such as `holon-stage.sh`) and never run disconnected manual stage commands.
4. **Canonical `--target-worktree` Flag**: Following Bean 0249, the CLI accepts strictly `--target-worktree <path>`
   (defaulting to `apps/holon-agentic-coder/main` or `apps/holon-coherence/main`). Naming the `main` worktree is valid
   and selects the repository and base branch, but **the flow never runs in the `main` worktree**: stages 4 and 5 check
   out the execution branch and commit calibration and ledger rows in the target worktree, and `main` must stay on
   `main`, identical to `origin/main`. The flow runs in a dedicated `flow-<slug>` worktree cut from `origin/main`.
   `scripts/run_holon_flow.py` creates it (`git worktree add --no-track -b flow-<slug> ../flow-<slug> origin/main`) and
   passes it as `--target-worktree`; when invoking `holon flow` directly, do the same. Remove the worktree after the PR
   merges. Legacy `--repo-dir` is completely removed and must never be passed.
5. **Wait Out a Named Reset, Then the Fallback Ladder (maintainer rule, 2026-11-11)**: If any stage or subagent
   encounters model credit exhaustion, session limits, rate limits, or HTTP 429 errors (`You've hit your session limit`,
   `insufficient_quota`, `RESOURCE_EXHAUSTED`), **do not stop or block**:
   - **When the error names its reset time** (e.g. `resets 5:40pm (Australia/Melbourne)` or a relative
     `Resets in 51m58s` as Antigravity prints; a daily or weekly window), **wait until about one minute after that reset
     and resume automatically from the checkpoint on the same agent and model**. `scripts/run_holon_flow.py` does this
     itself (`parse_limit_reset` / `wait_for_limit_reset`), logging it before it sleeps; a hand-driven stage follows the
     same rule. Never report such a stop as terminal and never wait for a human to type "continue".
   - **A parent or subagent that receives a quota failure naming a reset schedules the resume at once** (`schedule` with
     the reset plus one minute) in the same turn, before doing anything else; it never waits for the user to say
     "continue" (maintainer, 2026-11-24).
   - **When no reset time is named** (true credit exhaustion), step down the fallback ladder and continue the flow from
     the current stage or checkpoint:
   - **Fable needs a longer stall window (2026-11-23)**: launch `run_holon_flow.py` with `HOLON_TURN_STALL_SECONDS=600`
     when the model is `claude-fable-5-2`. With the default 90 s every reviewer was cut ("review stall budget of 90 s
     exceeded") because Fable thinks longer than that before it streams.
   - **Claude (`claude-agent`)**: `claude-fable-5-2` $\rightarrow$ `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6`
     $\rightarrow$ `claude-haiku-4-5`.
   - **Antigravity (`antigravity-agent`)**: `gemini-4-neon` $\rightarrow$ `gemini-4-argon` $\rightarrow$
     `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash` (use `gemini-4-neon` for all Holon coding tasks until tokens
     run out).
   - **Antigravity AGY Subagent Runtime**: `Model: "inherit"` / `"pro"` $\rightarrow$ `"flash"` $\rightarrow$
     `"flash_lite"`.
   - **No Cross-Runner Switch**: never switch `--agent` between `claude-agent` and `antigravity-agent` on your own. When
     the active runner's ladder is exhausted, `scripts/run_holon_flow.py` stops and reports. The maintainer decides
     whether to switch runner. A reset written without minutes (`resets 10am (UTC)`) counts as a named reset, so the
     flow waits for it.
6. **PR Creation & Calibration Report Inclusion**:
   - Once Stage 3 pushes the `E-.../_` execution branch, the PR is opened via `gh pr create` targeting `main`.
   - Stage 5 Calibration creates the `/calibrated` audit branch. The calibration report (`plans/P-*_calibration.md`)
     **MUST ALSO be included in the PR** (by fast-forwarding or merging the calibration commit into the PR head branch
     and pushing to `origin`) so it appears in the PR diff.
7. **Canonical 3-Ledger Conflict Resolution**: Target repositories maintain strictly three ledgers under
   `holon-knowledge/ledger/` (`intents.jsonl`, `plans.jsonl`, `executions.jsonl`). When concurrent PR merges cause
   ledger conflicts against `origin/main`, do not run test suites: keep main's ledger file exactly as on main, in main's
   order, append only the branch's own rows (ordered by `created_at` among themselves), never move or re-sort a row
   already on main, then commit and push.
8. **Human-Only Merge Boundary (Bean 0034 / Rule 8)**: Agents MUST NEVER merge a PR that targets `main` (`gh pr merge`
   is strictly forbidden). The subagent completes when Stage 5 calibration is included in the PR, confirms the PR is
   clean and mergeable, and notifies the parent agent that the PR is ready for human merge.

---

## 🛠️ Step-by-Step Execution Guide

### Step 0: Entrypoint Delegation — Spawn the Background Flow Subagent

Before executing any flow commands, evaluate the **Re-Entrancy Guard**:

- **Re-Entrancy Guard**: If the currently executing agent is _already_ the spawned `bean <id> - holon flow <slug>`
  subagent, **DO NOT spawn another nested subagent**. Proceed directly to
  [Step 1: Validate Prerequisites & Parameters](#step-1-validate-prerequisites--parameters).
- **Main Interactive Agent Delegation**: When the user (or parent session) requests running a flow (e.g.
  `/holon-flow <intent.json>`):
  1. Parse the intent file path, target worktree, and optional `--agent` and `--model`.
  2. Immediately spawn a single background **Holon Flow Subagent** via `invoke_subagent` and return control to the user
     in the same turn:

     ```json
     {
       "TypeName": "self",
       "Role": "bean <id> - holon flow <slug>",
       "Model": "<lowest-tier model, probed per .agents/model-tiers.md>",
       "Prompt": "You are the background Holon Flow Subagent for intent `<intent_path>` (target_worktree: `<target_worktree>`, agent: `<agent>`, model: `<model>`). Execute `.agents/skills/holon_flow/SKILL.md`. Because you are already the spawned Holon Flow Subagent, pass the Step 0 re-entrancy guard and proceed directly to Step 1. Drive the entire 5-stage Holon flow lifecycle (Intent -> Plan -> Execute -> Review Loop -> Calibration). Ensure PR creation, handle model fallback ladders on quota errors, verify that the calibration report is committed and pushed into the PR diff, check mergeability against target branch, and record state in `.subagent/flow_<slug>_state.json`. Do NOT send intermediate messages; call `send_message` to the parent agent ONLY ONCE upon terminal completion (PR approved, calibrated, and awaiting human merge) or an unresolvable blocker."
     }
     ```

---

### Step 1: Validate Prerequisites & Parameters

Inside the background subagent, perform pre-flight verification:

1. **Verify Global `holon` Binary**: Ensure `holon` is available in `PATH` (`which holon` $\rightarrow$
   `~/.local/bin/holon`).
2. **Verify Docker Daemon**: Ensure Docker is running (`docker info`).
3. **Verify Intent JSON**: Read and parse `<intent_path>`. Ensure `slug`, `goal`, and `description` are present, and
   that the `goal` contains this sentence verbatim: "Code is self-explaining: no docstrings and no comments except '#
   why:' comments that record a reason the code cannot show." (self-explaining-code invariant, maintainer, 2026-11-27);
   add it if missing. Give the intent a descriptive `slug` of up to 32 characters (lowercase, hyphen-separated); the
   engine rejects longer root slugs, and since the short branch names of PR #206 two levels of nested child intents with
   32-character slugs fit GitHub's 255-character ref limit (see `.agents/rules.md`, "Git ref names are limited to 255
   characters").
4. **Verify Target Worktree**: Ensure `--target-worktree` is a dedicated `flow-<slug>` worktree (never the `main`
   worktree itself) that exists and is a clean git repository. Create it from `origin/main` first if it does not exist.
5. **Intent check (bean 0508, PR #348)**: with the target worktree at current `origin/main`, run
   `holon intent-check <intent_path> --target-worktree <target_worktree>`. Add each companion file it lists as missing
   to the intent's scope (files only, never directories), or record in the bean why not. Proposed companions and
   warnings are advisory.
6. **Determine Runner & Model**:
   - Default agent: `antigravity-agent` (or `claude-agent`)
   - Default model: `gemini-4-neon` (fallback: `gemini-4-argon` $\rightarrow$ `gemini-4-hydrogen` $\rightarrow$
     `gemini-3.8-flash`, or `claude-fable-5-2` / `claude-opus-5-5`)

---

### Step 2: Execute the 5-Stage Flow

Execute the flow using the canonical `holon flow` CLI runner or the companion Python orchestrator:

```bash
# Direct CLI execution
holon flow <intent_path> \
  --target-worktree <target_worktree> \
  --agent <agent> \
  --model <model>
```

Or using the automated companion orchestrator:

```bash
python3 .agents/skills/holon_flow/scripts/run_holon_flow.py <intent_path> \
  --target-worktree <target_worktree> \
  --agent <agent> \
  --model <model>
```

#### Claude credentials are built in

For `--agent claude-agent`, `scripts/run_holon_flow.py` builds the container credentials itself (`scripts/flow_env.py`):
it reads the long-lived OAuth token from `CLAUDE_CODE_OAUTH_TOKEN`, then the legacy file
`~/.holon/secrets/claude-oauth-token` if it still exists, then the OS keychain entry (service `holon`, account
`claude-oauth-token`), which is where the engine keeps it since pull request #271, wraps it in `HOLON_AGENT_SETTINGS`
with the echo padding, and sets `HOLON_TOKEN_REDUCE=0` and `PYTHONUNBUFFERED=1` for the flow process. It also switches
on Claude Code's experimental code mode (`CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1`, in the flow process and in the settings
`env` the containers read); export `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=0` before launching to switch it off. The token
is never printed. Nothing needs exporting by hand, and an already-set `HOLON_AGENT_SETTINGS` is left alone. When no
credentials can be found the runner stops before dispatch with a message naming what is missing, instead of letting
every Stage 4 reviewer exit with code 1 and no reason.

#### Monitoring Stage Progress

The subagent monitors the output and checkpoint file at `<target_worktree>/.holon/flow/checkpoint-<slug>.json`:

1. **Stage 1 (Intent)**: Verifies `I-.../_` branch creation and `intents.jsonl` entry.
2. **Stage 2 (Plan)**: Verifies `P-.../_` branch, `plans/P-*.md`, and predicted EV in `plans.jsonl`.
3. **Stage 3 (Execute)**: Verifies `E-.../_` branch, code implementation, and `executions.jsonl`.
4. **Stage 4 (Review Loop & Resolver)**: In-container ensemble review passes and native resolver runs.
5. **Stage 5 (Calibration)**: `/calibrated` branch generated and `plans/P-*_calibration.md` written.

---

### Step 3: Handle Failures & Apply Model Fallback Ladder

If `holon flow` exits with an error:

1. **Quota / Credit / Session Limit Errors**: If the log contains `session limit`, `insufficient_quota`,
   `RESOURCE_EXHAUSTED`, or HTTP 429:
   - Identify the next tier down on the fallback ladder (e.g. `gemini-4-neon` $\rightarrow$ `gemini-4-argon`
     $\rightarrow$ `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash`, or `claude-opus-5-5` $\rightarrow$
     `claude-sonnet-4-6`).
   - Never switch `--agent` across runners without the maintainer's go-ahead; report the exhausted ladder instead.
   - Resume the flow using the saved checkpoint:

     ```bash
     holon flow <intent_path> \
       --target-worktree <target_worktree> \
       --agent <new_agent> \
       --model <new_model> \
       --checkpoint <target_worktree>/.holon/flow/checkpoint-<slug>.json
     ```

2. **Stage Timeout or Transient Blocker**: Once the underlying issue is resolved, resume from the interrupted stage:

   ```bash
   holon flow <intent_path> \
     --target-worktree <target_worktree> \
     --agent <agent> \
     --model <model> \
     --from-stage <stage>
   ```

---

### Step 4: Verify Pull Request & Stage 5 Calibration Inclusion

Once the flow finishes:

1. **Locate or Open PR**: Check if an open PR exists for the flow execution branch:

   ```bash
   gh pr list --repo <target_repo> --head "<execution_branch>/_"
   ```

   If not open, create the PR autonomously:

   ```bash
   gh pr create --repo <target_repo> --base main --head "<execution_branch>/_" \
     --title "<slug>: implementation" \
     --body "Automated Pull Request produced by Holon flow."
   ```

2. **Verify Calibration Report in PR Diff**: Verify that `plans/P-*_calibration.md` appears in the PR diff:

   ```bash
   gh pr diff <pr_number> --name-only | grep "_calibration.md"
   ```

   If the calibration report is committed on `<execution_branch>/calibrated` but not yet merged into the PR branch
   `<execution_branch>/_`, fast-forward or merge it:

   ```bash
   git -C <target_worktree> fetch origin
   git -C <target_worktree> checkout "<execution_branch>/_"
   git -C <target_worktree> merge --ff-only "<execution_branch>/calibrated"
   git -C <target_worktree> push origin "<execution_branch>/_"
   ```

3. **Verify Target Mergeability & Clean State**:

   ```bash
   gh pr view <pr_number> --json mergeable,mergeStateStatus
   ```

   **A flow is not finished while its PR conflicts with the target branch (maintainer, 2026-11-23).** If
   `mergeable == "CONFLICTING"` or `mergeStateStatus == "DIRTY"` at the end of the flow, including when the flow itself
   printed "completed successfully", do not report it as terminal. Rerun the flow:
   1. Resolve the conflict through the `resolve-conflict` skill in its own subagent (merge `origin/<target>`; never a
      rebase or force-push; ledger and KB conflicts mechanically; a code conflict that needs a decision goes back to the
      parent, which delegates a higher-tier resolve-conflict subagent). Push.
   2. Rerun the flow from the checkpoint, launched from the harness root, choosing the stage by what the merge did:
      - **Mechanical merge, PR's own diff unchanged** (ledger/KB only): rerun with
        `.agents/skills/holon_flow/scripts/run_holon_flow.py --from-stage calibrate`. Stage 5's merged-head gate
        compares the PR-own fingerprint with the one recorded at approval: when they match it keeps the approval, waits
        for CI on the merged head and redoes calibration; when they differ, or CI fails, it withdraws the consensus and
        restarts Stage 4 itself. **Do not use `--from-stage review` here**: it re-enters the review loop and dispatches
        the reviewers again even though nothing of the PR changed (seen on PR #258, 2026-11-23). Better still, for a
        ledger-only conflict skip step 1 and let the rerun's own conflict gate do the merge: it resolves ledgers itself
        and records the carry-over row.
      - **The PR's own diff changed** (a resolved code conflict), or the approval predates the fingerprint (it was
        recorded by an engine older than PR #254, so the checkpoint's consensus has no `approval_fingerprint`): rerun
        with `--from-stage review`; one fresh review records a fingerprinted approval, and later merges carry it over.
   3. Check mergeability again and repeat until the PR is `MERGEABLE` and `CLEAN` with green CI and the calibration
      report in the diff. If the target branch keeps moving, keep going; report only a conflict you cannot get resolved,
      never "ready" for a conflicting PR.

---

### Stage 3 overlap refusals are parked, not waited out (maintainer, 2026-11-26)

When Stage 3 admission refuses a plan because its touch set overlaps another flow in flight (or the flow otherwise waits
on another flow's PR), the flow does not hold a slot. Never add `--allow-overlap`. Run the wrapper with
`--no-wait-on-overlap` so it stops on the refusal, then park the flow: keep its worktree, branches and checkpoint, note
on its bean `parked <date>: blocked by <PR/flow> on <files>; resume from checkpoint when <condition>`, stop only this
flow's own processes, and end the subagent. Report the parked flow to the parent at once so the slot is reused. Resume
only from the checkpoint (`--checkpoint`) once the blocker merges or releases the files; never relaunch without
`--checkpoint`, which re-runs intent and plan and leaves duplicate `I-*` branches. Any other refusal (no touch set
declared, discovery unavailable) also stops and is reported.

### Push notifications (ntfy.sh)

`scripts/run_holon_flow.py` sends **one** push notification, and only when calibration is done: the flow exited cleanly
and its checkpoint records Stage 5 as completed (`white_check_mark`, through `scripts/notify_ntfy.py`). A flow that
stops, fails or waits on a usage limit sends nothing, and neither does the limit watcher. The topic is read from
`HOLON_NTFY_TOPIC` or `~/.holon/secrets/ntfy-topic` (mode 600, never committed or printed in reports; anyone who knows
it can read the messages). With no topic configured it silently does nothing. Messages stay on the ntfy server for a
while, so they carry only the intent slug and the PR number (no URL or repository name). Send a manual one with
`python3 .agents/skills/holon_flow/scripts/notify_ntfy.py "Title" "Message" --priority high`; use it after any hand-run
`holon calibrate` that the maintainer is waiting on, and only once calibration has finished.

### Step 5: Terminal Completion & Notification

0. **Wrapper gate and state file**: `run_holon_flow.py` itself exits non-zero when the flow exits 0 but the PR is
   missing, the calibration report is absent from the PR diff, or the PR is CONFLICTING/DIRTY, and waits (bounded, 45
   min, via `gh pr checks`) for pending checks before reporting success. It writes `.subagent/flow_<slug>_state.json`
   itself at the end (status, PR number/url, stage reached, consensus, calibration EV when logged, merge state, next
   action); the driver only reads it and may add fields. A merged PR is a clean finish. Dry runs skip all of this. A
   "spend limit" message is a quota error: with no reset time the wrapper steps down the ladder, with a named reset it
   waits.
1. **Write State Artifact**: Record completion summary to `.subagent/flow_<slug>_state.json`:

   ```json
   {
     "slug": "<slug>",
     "status": "COMPLETED",
     "pr_number": 138,
     "pr_url": "https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/138",
     "predicted_ev": 78.5,
     "actual_ev": 82.1,
     "delta_ev": "+3.6",
     "calibration_report": "plans/P-1794049540-antigravity-agent-gemini-3.8-flash-medium_calibration.md",
     "next_action": "awaiting_human_merge"
   }
   ```

2. **Notify Parent Agent**: Call `send_message` to the parent conversation ID **only once** upon terminal completion:

   ```text
   Holon Flow for '<slug>' has completed all 5 stages.
   - PR: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/<pr_number>
   - Consensus: APPROVED
   - Calibration: Included in PR diff (EV predicted: <pred>, actual: <act>, delta: <delta>)
   - Merge State: Clean & Mergeable
   - Next Action: Ready for human maintainer merge.
   ```
