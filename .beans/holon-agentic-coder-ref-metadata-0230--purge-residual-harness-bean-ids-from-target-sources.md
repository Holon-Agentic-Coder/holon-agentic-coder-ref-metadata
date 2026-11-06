# holon-agentic-coder-ref-metadata-0230

title: "Purge residual harness bean ids from holon-agentic-coder target sources" status: todo type: task priority: low
tags:

- holon-agentic-coder
- isolation
- rule-12
- deferred-findings
- pr123 created_at: 2026-11-05T12:00:00Z updated_at: 2026-11-05T12:00:00Z

---

## Summary

Deferral bean for PR #123's review loop (holon-agentic-coder). During the iteration-3 increment-scoped ensemble at head
2c12b92, reviewers 1 and 3 noted (out of increment, unchanged code) that harness task-tracker ids remain in
target-repository sources, violating AGENTS.md rule 12 (zero harness path/id leaks) hygiene:

- `apps/sandbox-executor/src/sandbox_executor/flow.py` — "Bean 0034", "Bean 0038", "Bean 0049", "Bean 0052", "Bean
  0063", "Bean 0085" in docstrings, comments and one runtime log/message string (e.g. lines 12, 1475, 3158, 3707, 4143,
  4262, 4494, 4615)
- `apps/sandbox-executor/src/sandbox_executor/local_llm.py` — bean id references in docstrings/comments
- `apps/sandbox-executor/tests/test_flow.py:473,1443,1529`
- `apps/sandbox-executor/README.md:43`

PR #123 itself removed "(Bean 0034)" from the review-loop template twins; these remaining occurrences are on code PR
#123 did not change, so they were dispositioned `rejected: deferred: unchanged code -> 0230` per pr-review-loop
principle 12 rule 1 and must be purged via a dedicated Holon flow intent (target-native wording only; no harness
references in the intent text).
