# Slot Keeper

`.agents/scripts/slot_keeper.py` refills flow slots without a model turn (bean 0592). Each invocation is one pass; a
timer or loop wrapper drives it every 60 s.

## Pass

1. Count live flows: distinct intents (or checkpoints) on `run_holon_flow.py` command lines in `ps`.
2. Read `todo/slot-queue.json`: an ordered list of
   `{bean, intent_path, kind: "new" | "resume", checkpoint?, blocked_by?, target_worktree?, own_pr?}`. Resume entries
   are evaluated before new ones.
3. For each entry, in order, hold it with a reason or launch it. Reasons: `already-live`, `cap`, `blocked_by:<bean>`,
   `check:<failure>` (intent missing or unreadable, empty scope, directory in scope, missing checkpoint) and
   `overlap:<file>:<holder>`, where the holder is `live:<intent>`, `parked:<bean>`, `launched:<bean>` or `pr:<number>`.
   Touch sets are the intent scope plus the Touch Set of the flow worktree's plan files; open pull request files come
   from `gh pr list`. A held new entry reserves nothing, so a disjoint entry is never held behind an overlapping one; a
   held resume entry (a parked flow) does reserve its files.
4. Launch in the background (`uv run python .agents/skills/holon_flow/scripts/run_holon_flow.py <intent> ...` with
   `--no-wait-on-overlap`, plus `--bean` for a new flow or `--checkpoint` for a resume) until the cap (8) is reached,
   with output in `todo/flow-<slug>.log`. Launched entries are removed from the queue file.
5. Append one line to `todo/slot-keeper.log`: `<ts> live=<n> cap=<n> launched=<this pass only> held=<bean:reason ...>`.

Run `uv run python .agents/scripts/slot_keeper.py --dry-run` to see the decisions without launching.

## Triggers and heartbeat

- `--loop-seconds 60` runs a pass every 60 s and also within 5 s of any `.subagent/flow_*_state.json` change (the
  wrapper writes it when a flow exits, including after calibration).
- `--check-heartbeat` exits 3 and appends to `todo/slot-keeper-alerts.log` when the last logged pass is over 120 s old;
  the launchd job below restarts a dead keeper through `KeepAlive`.

## launchd example (not installed)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>dev.holon.slot-keeper</string>
    <key>WorkingDirectory</key>
    <string>/path/to/holon-agentic-coder-ref-metadata</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/local/bin/uv</string>
      <string>run</string>
      <string>python</string>
      <string>.agents/scripts/slot_keeper.py</string>
      <string>--loop-seconds</string>
      <string>60</string>
    </array>
    <key>KeepAlive</key>
    <true />
    <key>StandardErrorPath</key>
    <string>todo/slot-keeper.stderr.log</string>
  </dict>
</plist>
```

A second job with `StartInterval` 60 and the `--check-heartbeat` argument raises the heartbeat notice.
