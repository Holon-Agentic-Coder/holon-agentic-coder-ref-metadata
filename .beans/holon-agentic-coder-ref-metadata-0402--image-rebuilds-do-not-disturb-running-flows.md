---
# holon-agentic-coder-ref-metadata-0402
title: "A post-merge image rebuild does not disturb flows that are running or starting"
status: todo
type: bug
priority: normal
tags:
  - harness
  - docker
  - post-merge
  - reliability
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-24T08:30:00Z
---

## Problem

After a pull request merges, the post-merge steps rebuild the agent images and reinstall the CLI in place. On 2026-11-24
the `holon/agent-claude` image was rebuilt at 07:45:07Z, the moment two flows left their overlap wait and started
containers; both aborted at pre-flight (Bean 0393). A flow can also start a stage on one image and finish it on another.

## Goal

- Images are built under a new tag and `latest` is switched only when the build is complete.
- A flow records the image it started with and keeps using it until it ends; the next flow picks up the new one.
- The post-merge skill does not rebuild while a flow is in pre-flight, or the engine tolerates it (Bean 0393).

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- The link between the rebuild and the slow pre-flight exit is probable, not confirmed (see Bean 0393).
- Harness side: the `install-holon`, `install-coherence` and `post-pr-merge` skills.
