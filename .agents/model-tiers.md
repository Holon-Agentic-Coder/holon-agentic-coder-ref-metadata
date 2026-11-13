# Model Tiers

Skills and delegated tasks name a **tier**, never a model. The model behind a tier changes as each harness ships new
ones, so it is **probed from the harness at the time of use**, never copied into a skill, a table or a settings file. A
frontmatter `model:` or a project-level model override (for example `CLAUDE_CODE_SUBAGENT_MODEL`) is a fixed name that
applies to one harness only and goes stale; do not use either.

| Tier       | Use it for                                                                                    |
| ---------- | --------------------------------------------------------------------------------------------- |
| **lowest** | Mechanical, script-driven or additive work: installs, cleanup, triage, limit maths, conflicts |
| **middle** | Multi-step work with real judgement                                                           |
| **top**    | Reviews, design and anything whose mistake is costly                                          |

## Finding the lowest tier

Run the probe for the harness you are running on. It asks the harness what it offers now and ranks the answer by generic
size markers in the model names (`nano`, `lite`, `mini`, then `flash`, `haiku`, `small`, then `sonnet`, then `pro`,
`opus`, `ultra`) and by effort suffix (`low` before `high`). It never relies on a model name or version, so a new
smaller model is found as soon as the harness lists it.

| Harness                         | Probe                                                                                                                                                                             |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Antigravity                     | `python3 .agents/scripts/lowest_model.py --probe antigravity` (reads `agy models`)                                                                                                |
| `holon` CLI (`--model`)         | `python3 .agents/scripts/lowest_model.py --probe holon --runner <runner>` (reads `holon models --json`)                                                                           |
| Claude Code and other harnesses | Read the model options your own subagent tool offers (for Claude Code, the `model` values of the `Agent` tool), then `python3 .agents/scripts/lowest_model.py --candidates a,b,c` |

The output is JSON: `lowest` (the model to use), `ranked` (every model the probe could rank) and `unranked` (names with
no size marker, never chosen as the lowest). Read `ranked` as a sanity check. If the harness offers models the probe
cannot rank, extend the markers in `lowest_model.py` rather than hard-coding a model in a skill.

Confirm the chosen model answers before relying on it (for Claude Code, a one-line
`claude -p --model <lowest> "reply ok"`). If the probe fails (exit 1), or the harness cannot pick a model per subagent,
run inline on the active model and say so in the report. Never fail the skill over it.

## How a skill uses it

A skill that declares **Model tier: lowest** runs as follows:

1. The parent agent probes for the lowest tier model, then starts a **dedicated subagent** on it and passes it the skill
   file plus the target (PR number, path, message). The subagent's output stays out of the parent's context; it returns
   a short report.
2. If the subagent cannot finish (an escalation the skill names, or repeated failure), re-run it one tier up: **lowest**
   $\rightarrow$ **middle** $\rightarrow$ **top**, matching the fallback ladders in `AGENTS.md`. The middle tier is the
   next family up in the same probe output; the top tier is the harness's strongest, or the session model.

Skills that carry no tier (the PR reviewers and the review loop, `answer`) run on the session's model.
