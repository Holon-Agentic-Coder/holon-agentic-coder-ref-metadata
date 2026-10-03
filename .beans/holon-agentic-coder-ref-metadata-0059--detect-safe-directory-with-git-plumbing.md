---
# holon-agentic-coder-ref-metadata-0059
title: "Detect safe.directory with git plumbing instead of substring-matching .git/config"
status: todo
type: task
priority: low
tags:
  - sandbox-executor
  - git
  - review-nit
created_at: 2026-09-28T05:10:00Z
updated_at: 2026-09-28T05:10:00Z
---

Finding F-6 from the PR #60 review loop (Bean 0019 slice A), deferred rather than fixed there because it is detection
only and the mechanism it detects for is correct.

## The defect

`apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` decides whether to add
`-c safe.directory=<repo_dir>` to a git invocation by opening `.git/config` and testing for the literal substring
`directory = {cwd}` (also accepting `directory = *`). `_repair_git_repo` then verifies its own work by reading that file
the same way, and falls back to hand-appending a `[safe]` section when the plumbing write fails.

Text-matching a git config file is fragile in ways that fail silently: quoted or escaped paths, a multi-value
`safe.directory` list, an included config (`include.path` / `includeIf`), or a value written by a different git version
with different whitespace. Each case sends the executor down the "still broken" branch, and in the worst case the
fallback hand-writes a config section that duplicates an existing one.

## Requested change

Query git instead of reading the file: `git config --local --get-all safe.directory` (compare entries after
`os.path.realpath`), and repair through `git config --local --add safe.directory <path>` only, deleting the
hand-written-config fallback in favour of reporting the failure. Behaviour must stay equivalent for the cases the
current tests pin, and the executor must keep working when the config is unwritable -- which is exactly why the fallback
exists, so the replacement should fall back to per-invocation `-c` for that run rather than to editing the file.

## Why the injection itself stays

Replacing the argument injection with `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_0` was proposed and rejected during the Bean
0019 review: those variables are not honoured by `git clone` on the git 2.47.3 shipped in `holon/orchestrator`, and the
`file://` transport applies `safe.directory` to `file://` sources too. That evidence is recorded in
`.subagent/holon-agentic-coder_pr60_coordination.json` and in the Bean 0019 stage-4 notes. Do not re-propose it without
new evidence against the current image.

## Notes

- Target repository: `holon-agentic-coder`, `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` plus
  `apps/sandbox-executor/tests/test_executor.py`.
- Small, self-contained; a good candidate to bundle with another sandbox-executor change.
- Changes must go through the flow, not a host-side hand edit.
