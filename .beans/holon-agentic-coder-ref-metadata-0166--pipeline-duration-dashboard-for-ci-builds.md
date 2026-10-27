---
# holon-agentic-coder-ref-metadata-0166
title: "Pipeline duration dashboard for CI builds"
status: todo
type: feature
priority: high
tags:
  - ci
  - performance
  - observability
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-27T07:57:13Z
updated_at: 2026-10-27T07:57:13Z
---

## Problem

There is no single view of how long each CI build takes over time. On 2026-10-26 the maintainer noticed the
holon-agentic-coder `unit (macos-latest)` job running past 10 minutes during PR #97. Finding the cause took manual
`gh api` queries across eleven heads: `main` was already at 662 s of pytest time, and per-run timings varied by about
±20% on hosted macOS runners. After the canary fix the job dropped to 262-438 s, but nothing records that trend or makes
it visible.

GitHub provides:

- per-run and per-job durations on each workflow run page;
- organisation-level "Actions performance metrics" (average run and job duration, queue time and failure rate per
  workflow or job; availability depends on plan, to be checked);
- the raw REST data (`/repos/{owner}/{repo}/actions/runs`, `/actions/runs/{id}/jobs`).

None of these gives per-job duration trends per branch or PR, per-test duration breakdowns, a marked ceiling or
baseline, or a link from a slowdown to the commit that caused it.

## Scope

1. **Check the built-in option first.** Look at the organisation's Insights → Actions performance metrics. Record what
   it covers and what plan it needs, and use it instead of building where it already answers the need.
2. **Collect.** Pull run and job start and end times, conclusion, head SHA, branch, PR number and runner OS for every
   workflow in `holon-agentic-coder` and `holon-coherence`. Use real data only (AGENTS.md item 10). Also collect pytest
   per-test durations where available, from the JUnit XML or `--durations` output published as artefacts (shared with
   Bean 0163).
3. **Dashboard.** Show, per job and runner OS, duration over time for `main` and for PR heads. Include:
   - the rolling-median baseline and the tolerance band from Bean 0163;
   - hard ceilings, such as 10 minutes for unit;
   - queue time against run time;
   - failure and flake markers (re-runs);
   - a drill-down from any point to the run, commit and PR;
   - the slowest tests for a selected run, and how they changed against the baseline.
4. **Freshness.** Fetch live data from the GitHub API, or refresh a snapshot on a schedule. Document which, and how to
   refresh it.
5. **Hosting.** Choose where it lives: a claude.ai dashboard artifact reading the API, GitHub Pages fed by a scheduled
   workflow, or similar. Record the decision.

## Notes

- Pairs with Bean 0163 (the CI timing regression gate). The gate enforces; this dashboard explains. Share the stored
  timing data and the baseline definition between the two.
- Related flakes: Beans 0154 and 0167 (turn-supervisor reader join). Re-runs should be visible on the dashboard.
- If it lives in a target repository, build it through the Holon flow, one flow per repository. A harness-side or
  artifact-hosted dashboard can be built directly.
