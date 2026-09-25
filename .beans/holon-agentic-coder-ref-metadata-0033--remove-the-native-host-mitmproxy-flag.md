---
# holon-agentic-coder-ref-metadata-0033
title: "Remove the --native host-mitmproxy flag"
status: completed
type: task
priority: normal
created_at: 2026-09-25T04:00:00Z
updated_at: 2026-09-25T05:18:00Z
---

`holon-coherence start --native` ("Run natively using host mitmproxy instead of Docker") should be deleted. It is an
undocumented, untested escape hatch whose original motivation -- that a containerized proxy cannot reach a local model
server -- no longer holds.

## Why it can go now

- **Docker-first is the architecture.** README "Quick Start (Docker-First Architecture)" and the container `ENTRYPOINT`
  define the supported path. The native branch is the only alternative and nothing documents it: `--native` appears in
  no README section, no `docs/` page, no `Makefile` target and no CI workflow.
- **The reason it existed is fixed properly.** Bean 0027 added `--local-llm-base` with
  `--add-host=host.docker.internal:host-gateway` and container-side address rewriting. Measured on 2026-09-25: through
  the containerized proxy, `localhost:8081`, `127.0.0.1:8081`, `[::1]:8081` and the host LAN address all reach a real
  vMLX server with HTTP 200 and full wire telemetry. Docker Desktop also forwards host **loopback-only** services via
  the gateway, so even an Ollama-style `127.0.0.1` bind is reachable from the container.
- **It was never reachable from the runners.** Scrapped Bean 0028 recorded that `RunnerFlags` never parsed `--native`,
  so `holon-coherence <agent> --native` silently passed the flag to the agent instead. Removing `--native` closes that
  trap rather than fixing it.
- **No test coverage, and a host-specific failure mode.** `tests/` never exercises the native branch. It is also the
  only path that dies on a broken virtualenv: `.venv/bin/mitmdump: bad interpreter` after the repo moved to `apps/`
  broke `--native` completely while the Docker path kept working (observed 2026-09-25).
- **Host-side cost.** Native mode needs the Holon CA trusted by the host and runs without container isolation, for a
  path nobody uses.

## Exact surface

| Location                                 | Content                                                     |
| ---------------------------------------- | ----------------------------------------------------------- |
| `src/holon_coherence/cli.py:1129`        | `start_parser.add_argument("--native", ...)`                |
| `src/holon_coherence/cli.py:1259`-`1260` | `# If running inside container or explicitly requested ...` |
| `pyproject.toml:29`                      | `native = ["mitmproxy==12.2.3"]` optional-dependency extra  |

## Constraints

- **Do not delete the container half of the branch.** `if is_in_container() or args.native:` is how the image itself
  starts mitmproxy -- the `Dockerfile` `ENTRYPOINT` runs `holon-coherence start --port 8080` inside the container. It
  must become `if is_in_container():` and keep working.
- Keep the `mitmproxy` dependency in the `dev` group (tests import `mitmproxy` types) and remember the image installs
  mitmproxy itself from `mitmproxy/mitmproxy:12.2.3`.
- Decide explicitly whether the `native` extra in `pyproject.toml` is removed with the flag; nothing in `README.md`,
  `Makefile`, `docs/` or CI references it, so removal looks safe but should be confirmed against any external install
  instructions.

## Acceptance criteria

- `holon-coherence start --native` fails as an unrecognized argument instead of launching host mitmproxy.
- `holon-coherence start`, `holon-coherence start -d` and the container `ENTRYPOINT` still bring up a healthy proxy
  (`holon-coherence status` / `wait_for_proxy_ready`), verified against a real Docker run.
- No remaining references to `--native` in code, help text, docs or Makefile.

## Test coverage

- Assert `--native` is no longer accepted by the `start` parser.
- Keep/extend a test that `is_in_container()` alone still selects the mitmproxy launch path, since that is what the
  container relies on.
- Re-run the Docker integration test (`pytest -m integration_test`) to prove the container entry path is unaffected.

## Notes

- Target repository: `holon-coherence`. Work in a dedicated worktree off `origin/main` (autonomous worktree creation is
  allowed; never touch the `main` worktree -- see AGENTS.md rule 5).
- Related: Bean 0027 (`--local-llm-base`, which supersedes this flag's purpose), Bean 0028 (scrapped; documented that
  `--native` was unreachable from the runner path).

## Resolution

Done 2026-09-25 in worktree `apps/holon-coherence/chore-0033-remove-native-flag`, branch
`chore/0033-remove-native-flag`, squashed to one commit and pushed to `origin` (PR not raised -- maintainer's call).
Filed as `k4t7`, renamed to `0033` by the maintainer; the worktree and branch follow the renamed id.

- `src/holon_coherence/cli.py`: `--native` argument removed; the direct-mitmproxy branch is now `if is_in_container():`
  with a comment naming the `ENTRYPOINT` as its reason for existing.
- `pyproject.toml`: `native` optional-dependency extra removed (nothing referenced it), `uv.lock` regenerated -- the
  root package no longer advertises `provides-extras = ["native"]`.
- `tests/test_cli.py`: added `test_start_command_rejects_removed_native_flag` (argparse exits 2 with
  `unrecognized arguments: --native`) and `test_in_container_start_still_launches_mitmproxy_directly`, which asserts the
  in-container branch launches `mitmdump -s .../mitm_addon.py --listen-port 8080` and invokes **no** Docker command.
- Verified: 145 tests pass, `ruff check`/`format --check` clean, `holon-coherence start --help` no longer lists the
  flag, and a real container built from this branch still comes up via the image `ENTRYPOINT`
  (`Loading script .../holon_coherence/mitm_addon.py`, `HTTP(S) proxy listening at *:8080`, request through it returned
  200).

Kept deliberately: the `mitmproxy` pin in the `dev` dependency group (tests import mitmproxy) and the image's own
mitmproxy from `mitmproxy/mitmproxy:12.2.3`.

Note: `apps/holon-coherence/main/AGENTS.md` still carries its own push/branch guidance written before the per-agent
worktree rules; updating that file means a commit inside the `holon-coherence` repo, which was not done here because it
is out of scope for this bean and that text lives in the `main` worktree.
