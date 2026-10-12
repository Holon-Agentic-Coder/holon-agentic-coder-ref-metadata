---
# holon-agentic-coder-ref-metadata-0091
title: "Remove yq and yamllint requirements and use Prettier for YAML validation"
status: completed
type: task
priority: normal
tags:
  - makefile
  - hygiene
  - linter
  - prettier
  - yaml
created_at: 2026-10-13T13:23:00Z
updated_at: 2026-10-14T23:31:00Z
---

Remove the dependency on external binary tools `yq` and `yamllint` in `Makefile` and CI pipelines, replacing or
consolidating YAML validation to use Prettier (`npx prettier --check` / `prettier --write`).

## Background & Context

In `holon-agentic-coder`'s `Makefile`, `lint-yaml` executes:

```makefile
lint-yaml:
	@if [ -n "$(DRY_RUN)" ]; then exit 0; fi; \
	echo "$(COLOR_BOLD)Validating YAML files with yq...$(COLOR_RESET)"; \
	FILES=$$(find $(LINT_TARGET) -type d \( -name ".git" -o -name ".venv" -o -name "holon-coherence" \) -prune -o -type f \( -name "*.yml" -o -name "*.yaml" \) -print); \
	for file in $$FILES; do \
		if command -v yq >/dev/null 2>&1; then \
			yq -e 'true' "$$file" >/dev/null 2>&1 || { echo "$(COLOR_RED)❌ YAML validation failed for $$file$(COLOR_RESET)"; exit 1; }; \
		elif command -v yamllint >/dev/null 2>&1; then \
			yamllint -d relaxed "$$file" >/dev/null 2>&1 || { echo "$(COLOR_RED)❌ YAML validation failed for $$file$(COLOR_RESET)"; exit 1; }; \
		else \
			echo "$(COLOR_RED)❌ Neither yq nor yamllint is available to validate $$file$(COLOR_RESET)"; exit 1; \
		fi; \
	done; \
	echo "$(COLOR_GREEN)✅ All YAML files are valid.$(COLOR_RESET)"
```

- When running on a host environment or sandbox where `yq` or `yamllint` is not installed, running `make lint` fails
  abruptly even though Node.js and `npx prettier` (used by `lint-md`) are already present.
- Prettier natively supports YAML parsing and validation out of the box (`--parser yaml` or matching `**/*.{yml,yaml}`).
  Any malformed YAML syntax fails `prettier --check` with a parse error and line number.
- `yq` installation was previously baked into Dockerfiles (e.g. Bean 0085 pinned `yq` v4.44.1). Removing `yq` and
  `yamllint` simplifies Docker image footprints, local onboarding, and Makefile targets.

## Requirements

1. **Update `Makefile`**:
   - Refactor `lint-yaml` to validate YAML files using Prettier (`npx prettier --check` or bundled prettier invocation).
   - Alternatively, consolidate `lint-yaml` and `lint-md` into a single Prettier hygiene check covering
     `**/*.{md,yml,yaml}` or maintain `lint-yaml` using `npx prettier --check "$$file"`.
   - Ensure `make lint` passes cleanly out-of-the-box on machines without `yq` or `yamllint`.
2. **Update Dockerfiles & Image Tooling**:
   - Remove `yq` installation steps from Dockerfiles (`apps/sandbox-executor/docker/Dockerfile.agent-base` or relevant
     sandbox images) and package installer scripts if no longer needed elsewhere.
3. **Update CI Workflows**:
   - Ensure `.github/workflows/test-hygiene.yml` and `make lint` pass without needing `yq` installed on runner
     instances.
4. **Update Documentation & Tests**:
   - Update `test_makefile.py` to test the new Prettier-based `lint-yaml` target.
   - Update documentation references in `docs/` and `Makefile` help strings.

## Notes

- Target repository: `Holon-Agentic-Coder/holon-agentic-coder`
- Related beans: Bean 0085 (executor toolbelt linters), Bean 0088 (hygiene format and CI).

## Resolution

- In `Makefile`:
  - Refactored `lint-yaml` to validate YAML files using `xargs npx prettier --check` with unsuppressed stderr error
    diagnostics.
  - Updated `lint-yaml` help text to document Prettier validation.
  - Removed `yq` and `yamllint` from required tools list in `tools` target.
- In `apps/sandbox-executor/Dockerfile`:
  - Removed `yamllint` from `apt-get install`.
  - Removed static binary `yq` download and installation steps.
- In `.github/workflows/test-hygiene.yml`:
  - Removed `yamllint` and `yq` installation steps.
- In `.agents/AGENTS.md`:
  - Updated toolbelt instructions to specify Prettier for YAML formatting and validation, removing `yq` and `yamllint`.
- In `apps/sandbox-executor/tests/test_makefile.py`:
  - Removed `yq` and `yamllint` stubs from `_create_mock_toolbelt` and `test_tools_target_reports_paths_and_versions`.
  - Updated `test_lint_yaml_fails_on_malformed_fixture` to assert Prettier execution.
- Delivered via Holon flow PR #75 (`I-1791978544-submodule-update-and-prettier-yaml`). All 10 CI checks pass green, 549
  unit tests pass, 3-agent ensemble consensus approved, calibrated ($\Delta EV$ +4.72). Merged into `main` (commit
  `8c81f68`).
