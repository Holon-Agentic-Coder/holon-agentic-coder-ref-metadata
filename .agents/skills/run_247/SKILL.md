---
name: run_247
description:
  Computes when a coding-agent (Claude, Codex, Antigravity, ...) usage limit resets and when to resume. Use when a run
  dies on a limit message naming a reset time.
---

# run_247

```bash
python3 .agents/skills/run_247/scripts/limit_reset.py --runner <name> "<limit message>"
```

Prints JSON: `reset_at`, `resume_at` (reset + 1 min), `seconds_until_resume`, `kind`, `kind_source`, `label`.

- Exit `0`: wait until `resume_at`, then resume the same model from the checkpoint.
- Exit `1` (no reset named): credit exhaustion. Step down the model ladder or switch runner; do not wait.
- `kind` is the message's own label (`weekly limit`), else the label of the runner's single `resets.json` entry when its
  reset matches this one, else `unknown`. Never guessed. Each labelled message replaces that runner's entry
  (`--no-record` skips).
- Parses `reset(s) <time|date|weekday|in N hours M minutes>`. Other wordings exit `1` until extended.
- `--self-test` checks the parser.

## Background watcher (`watch_limits.py`)

`/run_247` needs a live session, so it cannot help once the session's own tokens are gone. `scripts/watch_limits.py`
runs outside Claude: it tails `.subagent/flow_*.log`, runs the same parser on each limit message, announces it once
through ntfy (`resume_at`, or credit exhaustion when no reset is named) and, with `--relaunch`, relaunches a stopped
`claude-agent` flow from its checkpoint after `resume_at` (same agent and model, `HOLON_TOKEN_REDUCE=0`, OAuth token
from the secrets file, never printed). Review loops are conversation-driven, so they are announced only, never resumed.

- Try it: `python3 .agents/skills/run_247/scripts/watch_limits.py --once --dry-run`; `--self-test` checks it.
- Run it permanently: copy `scripts/com.holon.limit-watch.plist` to `~/Library/LaunchAgents/`, create
  `~/.holon/limit-watch/`, then `launchctl load ~/Library/LaunchAgents/com.holon.limit-watch.plist`. State is kept in
  `~/.holon/limit-watch/state.json`; history before the first poll is not announced.
