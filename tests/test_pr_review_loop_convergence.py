"""Unit tests for pr-review-loop convergence rules (Bean 0170) and orchestrator subagent delegation (Bean 0212)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PR_REVIEW_LOOP_SKILL = REPO_ROOT / ".agents" / "skills" / "pr_review_loop" / "SKILL.md"
PR_REVIEWER_SKILL = REPO_ROOT / ".agents" / "skills" / "pr_reviewer" / "SKILL.md"
COORDINATION_DOC = REPO_ROOT / ".agents" / "coordination.md"


class TestPrReviewLoopConvergenceAndDelegation:
    """Verify Step 0 orchestrator subagent delegation (Bean 0212) and Principle 12 convergence rules (Bean 0170)."""

    def test_pr_review_loop_defines_step_0_orchestrator_delegation(self) -> None:
        text = PR_REVIEW_LOOP_SKILL.read_text(encoding="utf-8")

        assert "### Step 0: Entrypoint Delegation — Spawn the Background Loop Orchestrator Subagent" in text
        assert text.index("### Step 0:") < text.index("### Step 1: Parse Parameters")
        assert 'Role: "PR Review Loop Orchestrator (<repo> PR #<N>)"' in text
        assert '"TypeName": "self"' in text
        assert '"Model": "inherit"' in text
        assert "invoke_subagent" in text
        assert "MUST NOT execute the loop inline" in text

    def test_pr_review_loop_defines_reentrancy_guard_and_terminal_notification(self) -> None:
        text = PR_REVIEW_LOOP_SKILL.read_text(encoding="utf-8")

        assert "Re-Entrancy Guard" in text
        assert "DO NOT spawn another nested loop orchestrator" in text
        assert "send_message" in text
        assert "MAX_ITERATIONS_REACHED" in text
        assert "DIVERGING" in text

    def test_pr_review_loop_defines_principle_12_convergence_rules(self) -> None:
        text = PR_REVIEW_LOOP_SKILL.read_text(encoding="utf-8")

        assert "12. **Convergence Rules (Bean 0170)**:" in text
        assert "Increment-scoped review after the first full ensemble." in text
        assert "Bounded mutation work." in text
        assert "Scope freeze." in text
        assert "Single source for behaviour docs." in text
        assert "Convergence report." in text
        assert "voted_head" in text
        assert "deferral_bean" in text
        assert "mutation_sweeps" in text
        assert "<repo>_pr<N>_convergence_report.md" in text

    def test_pr_reviewer_defines_increment_scoped_mode(self) -> None:
        text = PR_REVIEWER_SKILL.read_text(encoding="utf-8")

        assert "### Step 2a: Determine the Review Scope (Full vs Increment-Scoped Mode)" in text
        assert "voted_head" in text
        assert "deferred_findings" in text

    def test_coordination_doc_defines_two_tier_review_loop_delegation(self) -> None:
        text = COORDINATION_DOC.read_text(encoding="utf-8")

        assert "### 2. Review Loop Delegation" in text
        assert "2-tier subagent delegation architecture" in text
        assert "Tier 1 (Main Interactive Agent -> Background Loop Orchestrator)" in text
        assert "Tier 2 (`PR Review Loop Orchestrator` Subagent -> Per-Pass Reviewer & Resolver Subagents)" in text
        assert 'Role: "PR Review Loop Orchestrator (<repo> PR #<N>)"' in text
        assert "Re-Entrancy Guard" in text
