---
# holon-agentic-coder-ref-metadata-0548
title: "Review-loop git identity env (PR #350) leaks into the resolver pre-push test run and fails two hermetic tests"
status: scrapped
type: bug
priority: high
tags:
  - holon-agentic-coder
  - review-loop
  - tests
created_at: 2026-11-26T21:30:00Z
updated_at: 2026-11-26T21:30:00Z
---

## Evidence

Flow main-push-superseded-skip (PR #353), Stage 4 iteration 1, twice: `Resolver pre-push test failed`, 2 failed / 9091
passed, while the same two tests pass on the host.

- `tests/test_flow_repo_templates.py::test_the_history_matches_build_flow_repos_and_commit_on`: expected author
  `Holon Test`, got `Holon Review Loop Agent review-loop-agent@holon-agentic-coder.com`.
- `tests/test_executor_run_salvage.py::TestExecutorPartialWorkSalvage::test_agent_commits_with_clean_tree_record_the_agent_head`:
  `review-loop-agent@...` != `executor-agent@...`.

Cause: PR #350 (review loop identity via GIT_AUTHOR_* and GIT_COMMITTER_* process environment) leaves those variables in
the review-loop entrypoint's environment, and the resolver's pre-push pytest run inherits them; they override the
identity the hermetic tests configure. Every flow whose resolver runs the full suite after #350 will halt Stage 4 at its
first iteration (PR #352 is exposed too).

## Proposed fix

Apply the identity env only to the git commands the loop runs (a per-call env), or strip GIT_AUTHOR__, GIT_COMMITTER__
from the environment of the pre-push test subprocess and make the hermetic test helpers scrub them. Add a test that the
pytest subprocess env carries none of the four variables.

## Scrapped (coordinator, 2026-11-26)

Duplicate of Bean 0547 (same leak, logged minutes apart by another flow). Evidence folded into 0547.
