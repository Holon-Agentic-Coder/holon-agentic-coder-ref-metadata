---
# holon-agentic-coder-ref-metadata-0382
title: "The model alias 'fable' resolves to claude-opus-5-5; add claude-fable-5-2 to the model registry"
status: todo
type: bug
priority: high
tags:
  - models
  - runner
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-23T12:40:00Z
---

## Problem

`apps/sandbox-executor/src/sandbox_executor/agent_defaults.py` lists `"fable"` as an alias of the `claude-opus-5-5`
capability (`aliases=["opus", "claude-opus", "fable"]`). `--model fable` therefore runs Opus silently, although the
maintainer's flow model is Fable 5.2 (2026-11-23). There is no `claude-fable-5-2` entry; the full id only works because
unknown ids are passed to the claude CLI verbatim.

## Goal

- A `claude-fable-5-2` capability entry with aliases `fable` and `claude-fable`; `fable` no longer aliases Opus.
- `holon doctor` and the resolved-model log line show the canonical id a flag or alias resolved to.
- A test asserts every alias resolves to a model of the same family as its name.
- Related: Bean 0270 (discover runner models dynamically) would remove the hand-kept list; this bean is the small fix.
