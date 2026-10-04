---
id: "0068"
title: Remove develop branch triggers from all CI/CD workflows
status: completed
created_at: 2026-10-05T07:45:00Z
updated_at: 2026-10-05T07:55:00Z
labels:
  - ci
  - workflows
  - holon-agentic-coder
---

# Remove develop branch triggers from all CI/CD workflows

## Context

All GitHub Actions workflows in `holon-agentic-coder` were originally configured to trigger on both `main` and `develop`
branches for pushes and pull requests. In practice, all trunk development and PR flows target `main` directly, and
maintaining unused `develop` trigger rules added unnecessary clutter and risk of divergent branch behavior.

## Implementation

1. **Workflow Triggers**:
   - Removed `- develop` from push and pull_request branch filters across:
     - `.github/workflows/make.yml`
     - `.github/workflows/test-hygiene.yml`
     - `.github/workflows/test-integration.yml`
     - `.github/workflows/test-stress.yml`
     - `.github/workflows/test-unit.yml`

2. **Documentation Alignment**:
   - Updated `.github/workflows/README.md` to remove all mentions of `develop` and state that workflows trigger on
     `main`.
   - Updated branch protection recommendations in the README to reference `main` exclusively.

## Resolution

Resolved via commit `570d492` on PR #63:

- Re-calibrated with `holon calibrate` (Actual EV: 93.61, ΔEV: +7.66).
- Carried report onto PR branch in commit `00b8606` and pushed to origin.
