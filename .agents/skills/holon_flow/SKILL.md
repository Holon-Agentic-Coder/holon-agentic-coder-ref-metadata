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
   with `TypeName: "self"`, `Role: "Holon Flow Subagent (<slug>)"`, `Model` = the lowest tier per
   `.agents/model-tiers.md`) and immediately returns control to the user.
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
   - **When the error names its reset time** (e.g. `resets 5:40pm (Australia/Melbourne)` — a daily or weekly window),
     **wait until about one minute after that reset and resume automatically from the checkpoint on the same agent and
     model**. `scripts/run_holon_flow.py` does this itself (`parse_limit_reset` / `wait_for_limit_reset`), logging it
     before it sleeps; a hand-driven stage follows the same rule. Never report such a stop as terminal and never wait
     for a human to type "continue".
   - **When no reset time is named** (true credit exhaustion), step down the fallback ladder and continue the flow from
     the current stage or checkpoint:
   - **Claude (`claude-agent`)**: `claude-fable-5` $\rightarrow$ `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6`
     $\rightarrow$ `claude-haiku-4-5`.
   - **Antigravity (`antigravity-agent`)**: `gemini-3.8-pro-high` $\rightarrow$ `gemini-3.8-pro` $\rightarrow$
     `gemini-3.8-flash-medium` $\rightarrow$ `gemini-3.8-flash`.
   - **Antigravity AGY Subagent Runtime**: `Model: "inherit"` / `"pro"` $\rightarrow$ `"flash"` $\rightarrow$
     `"flash_lite"`.
   - **Cross-Runner Fallback**: If an account-wide limit is hit on the active runner, switch `--agent` between
     `antigravity-agent` $\leftrightarrow$ `claude-agent` and resume execution on the existing flow branch.
6. **PR Creation & Calibration Report Inclusion**:
   - Once Stage 3 pushes the `E-.../_` execution branch, the PR is opened via `gh pr create` targeting `main`.
   - Stage 5 Calibration creates the `/calibrated` audit branch. The calibration report (`plans/P-*_calibration.md`)
     **MUST ALSO be included in the PR** (by fast-forwarding or merging the calibration commit into the PR head branch
     and pushing to `origin`) so it appears in the PR diff.
7. **Canonical 3-Ledger Conflict Resolution**: Target repositories maintain strictly three ledgers under
   `holon-knowledge/ledger/` (`intents.jsonl`, `plans.jsonl`, `executions.jsonl`). When concurrent PR merges cause
   ledger conflicts against `origin/main`, do not run test suites: interleave the JSONL records chronologically by their
   `created_at` timestamp, commit, and push.
8. **Human-Only Merge Boundary (Bean 0034 / Rule 8)**: Agents MUST NEVER merge a PR that targets `main` (`gh pr merge`
   is strictly forbidden). The subagent completes when Stage 5 calibration is included in the PR, confirms the PR is
   clean and mergeable, and notifies the parent agent that the PR is ready for human merge.

---

## 🛠️ Step-by-Step Execution Guide

### Step 0: Entrypoint Delegation — Spawn the Background Flow Subagent

Before executing any flow commands, evaluate the **Re-Entrancy Guard**:

- **Re-Entrancy Guard**: If the currently executing agent is _already_ the spawned `Holon Flow Subagent (<slug>)`, **DO
  NOT spawn another nested subagent**. Proceed directly to
  [Step 1: Validate Prerequisites & Parameters](#step-1-validate-prerequisites--parameters).
- **Main Interactive Agent Delegation**: When the user (or parent session) requests running a flow (e.g.
  `/holon-flow <intent.json>`):
  1. Parse the intent file path, target worktree, and optional `--agent` and `--model`.
  2. Immediately spawn a single background **Holon Flow Subagent** via `invoke_subagent` and return control to the user
     in the same turn:

     ```json
     {
       "TypeName": "self",
       "Role": "Holon Flow Subagent (<slug>)",
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
3. **Verify Intent JSON**: Read and parse `<intent_path>`. Ensure `slug`, `goal`, and `description` are present. Keep
   the `slug` short (8 characters or fewer when the work may decompose): GitHub rejects any full ref over 255
   characters, `refs/heads/` included, and nested child branch names repeat the slug and the agent and model labels (see
   `.agents/rules.md`, "Git ref names are limited to 255 characters").
4. **Verify Target Worktree**: Ensure `--target-worktree` is a dedicated `flow-<slug>` worktree (never the `main`
   worktree itself) that exists and is a clean git repository. Create it from `origin/main` first if it does not exist.
5. **Determine Runner & Model**:
   - Default agent: `antigravity-agent` (or `claude-agent`)
   - Default model: `gemini-3.8-flash-medium` (or `claude-fable-5` / `claude-opus-5-5`)

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
it reads the long-lived OAuth token from `CLAUDE_CODE_OAUTH_TOKEN` or `~/.holon/secrets/claude-oauth-token`, wraps it in
`HOLON_AGENT_SETTINGS` with the echo padding, and sets `HOLON_TOKEN_REDUCE=0` and `PYTHONUNBUFFERED=1` for the flow
process. The token is never printed. Nothing needs exporting by hand, and an already-set `HOLON_AGENT_SETTINGS` is left
alone. When no credentials can be found the runner stops before dispatch with a message naming what is missing, instead
of letting every Stage 4 reviewer exit with code 1 and no reason.

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
   - Identify the next tier down on the fallback ladder (e.g. `gemini-3.8-pro` $\rightarrow$ `gemini-3.8-flash-medium`
     $\rightarrow$ `gemini-3.8-flash`, or `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6`).
   - Switch `--agent` across runners if all tiers on the active runner share an exhausted account quota.
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

   If `mergeable == "CONFLICTING"`, fetch `origin/main`, merge `origin/main` into the PR execution branch, resolve the
   ledger conflicts chronologically by `created_at`, commit, and push to origin.

---

### Push notifications (ntfy.sh)

`scripts/run_holon_flow.py` sends **one** push notification, and only when calibration is done: the flow exited cleanly
and its checkpoint records Stage 5 as completed (`white_check_mark`, through `scripts/notify_ntfy.py`). A flow that
stops, fails or waits on a usage limit sends nothing, and neither does the limit watcher. The topic is read from
`HOLON_NTFY_TOPIC` or `~/.holon/secrets/ntfy-topic` (mode 600, never committed or printed in reports; anyone who knows
it can read the messages). With no topic configured it silently does nothing. Messages stay on the ntfy server for a
while, so they carry only the intent slug. Send a manual one with
`python3 .agents/skills/holon_flow/scripts/notify_ntfy.py "Title" "Message" --priority high`; use it after any hand-run
`holon calibrate` that the maintainer is waiting on, and only once calibration has finished.

### Step 5: Terminal Completion & Notification

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
