---
# holon-agentic-coder-ref-metadata-0164
title: "Plain-language documentation for entropy, Expected Value, and how they relate"
status: completed
type: task
priority: normal
tags:
  - documentation
  - metrics
  - entropy
  - expected-value
  - holon-agentic-coder
created_at: 2026-10-26T13:08:18Z
updated_at: 2026-10-29T06:40:00Z
---

## Problem

The EV and entropy physics that drive every Holon flow decision are documented only in formula-first form
(`docs/metrics.md`, `holon-config/metrics/README.md`): weighted sums, LaTeX, and coefficient tables. There is no
explanation a newcomer can read and understand without already knowing the maths. The maintainer wants a plain-language
explainer in the `holon-agentic-coder` documentation that anyone with a high-school education can follow.

## Scope

Add a plain-language section to the `holon-agentic-coder` documentation (a new lead-in section at the top of
`docs/metrics.md`, or a short `docs/metrics-explained.md` that `docs/metrics.md` links to — the planner decides) that
explains, in everyday English:

1. **What entropy means here.** Entropy is a score for how much mess and risk a change creates while it is being made:
   how much code it touches, how hard it is to undo, how likely it is to collide with someone else's work, how likely it
   is to break out of its sandbox, and how unfamiliar the territory is. A small, familiar, easily reverted change has
   low entropy; a sprawling, destructive, conflict-prone change in unknown code has high entropy.
2. **What Expected Value (EV) means here.** EV answers "is this plan worth doing?": how likely it is to succeed and how
   much good it does if it succeeds, plus what the system learns by doing it, minus the mess it makes (entropy) and what
   it costs. High EV means "probably worth it"; low EV means "probably not, at least not this way".
3. **How they relate.** Entropy sits inside EV as a penalty, so the goal is not "zero mess" — a trivial change has
   almost no entropy but almost no value either. The goal is the most value for the least mess: the best plans and PRs
   maximise EV per unit of entropy. When valuable work is unavoidably messy, the flow does not abandon it; it splits the
   work into smaller pieces so each piece lands back in the low-entropy, high-EV corner.
4. **What the entropy budget does.** Every intent carries a mess allowance (`entropy_budget`, default 15.0). A plan
   predicted to exceed it must be decomposed into sub-intents before execution instead of being run as one big job.
5. **One worked example with real numbers**, e.g. Bean 0151's plan (EV 19.82, predicted entropy 12.6 against a budget of
   16.0): a large footprint that is still clearly worth it, and within budget.

Keep the existing formal reference intact; the plain-language section complements it and cross-links to it. An analogy
is welcome (e.g. building LEGO in a shared room: entropy is the size of the mess you make while building, EV is how cool
the finished model is minus that mess and the time it takes, and the budget is how much mess you are allowed before you
must split the build into smaller boxes) — but every analogy must be followed by the precise sentence it stands for.

## Notes

- Target repository: `holon-agentic-coder` (documentation only, no behaviour change). The change MUST go through the
  5-stage Holon flow; this bean is the harness record of the intent.
- Primary sources to stay consistent with: `docs/metrics.md`, `holon-config/metrics/README.md`,
  `holon-config/metrics/ev_config.json` (lambda 0.3, mu 0.5), `holon-config/metrics/entropy_config.json` (w1_ssa 0.30,
  w2_irr 0.25, w3_cl 0.20, w4_ser 0.15, w5_nov 0.10), and the EV formula
  `EV = P(success) * Impact + mu * LearningValue - lambda * dS_intent - Cost`.
- Plain-language glossary to use for the five entropy factors: State Surface Area = "how much code it touches";
  Irreversibility = "how hard it is to undo"; Conflict Likelihood = "how likely it collides with other work"; Sandbox
  Escape Risk = "how likely it breaks out of its safety sandbox"; Novelty = "how unfamiliar the territory is".
- Readability bar: a reader with a high-school education and no maths beyond arithmetic should be able to answer "what
  is entropy here, what is EV, and why does high entropy lower EV?" after one read. No LaTeX in the plain-language
  section; the formula may appear once in words and once in symbols.
- Low entropy by its own definition: documentation-only, no migrations, disjoint from the `flow.py`/`cli.py` sequential
  lane, so it can run in the parallel lane alongside code flows.
- Related: Bean 0041 (first-principles flow lifecycle reference, where EV/entropy documentation gaps were first noted),
  Beans 0065/0083/0146 (calibration reads of predicted vs observed entropy), Bean 0159 (entropy budget gate).

## Resolution

Completed through the 5-stage Holon flow on `holon-agentic-coder`:

- **Flow**: `I-1793246459-plain-language-entropy-and-expected-value-explainer` →
  `P-1793246475-claude-agent-claude-opus-5-5` → `E-1793246639-claude-agent-claude-opus-5-5`.
- **PR #106** (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/106): added `docs/metrics-explained.md`
  and linked it from `docs/metrics.md`. Converged in 6 review-loop iterations (3/3 ensemble approval at `90ee0ba`,
  review `5692923254`, 10/10 CI green), Stage 5 calibrated (`86e6031`, EV 45.32 predicted / 54.07 actual,
  Prettier-formatted in `553fe43`), synced with `main` in `38f1e30`, and merged by the maintainer as `956b4fd`
  (2026-10-29T05:45:58Z).
