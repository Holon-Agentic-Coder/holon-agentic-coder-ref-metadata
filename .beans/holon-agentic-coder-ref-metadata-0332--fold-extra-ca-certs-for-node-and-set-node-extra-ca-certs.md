---
id: "0332"
title: "Fold /usr/local/share/ca-certificates into ~/.config/node/node-extra-ca.pem and configure NODE_EXTRA_CA_CERTS"
status: completed
created_at: 2026-11-19T14:04:00+11:00
updated_at: 2026-11-19T21:45:00+11:00
tags:
  - dev-env
  - node
  - ssl
  - ca-certificates
  - ansible
  - dotfiles
  - feature
---

# 0332 - Fold /usr/local/share/ca-certificates into ~/.config/node/node-extra-ca.pem and configure NODE_EXTRA_CA_CERTS

## Problem Statement

Behind corporate TLS-inspecting proxies (where custom root/intermediate CA certificates live in
`/usr/local/share/ca-certificates`), Node.js uses its own compiled-in root certificate store unless
`NODE_EXTRA_CA_CERTS` points to a PEM file containing the additional CA certificates. Previously, `dev-env` injected
custom CA certificates into Conda's `cacert.pem`, leaving Node.js (and Node-based CLIs / Mason / npm tools) without
corporate CA trust.

## Scope of Changes

1. **Fold Custom CA Certificates for Node (`ansible/roles/node/tasks/main.yml`)**:
   - Check whether `/usr/local/share/ca-certificates` exists and is a directory (`stat`).
   - Find all `*.crt` and `*.pem` files under `/usr/local/share/ca-certificates` (`recurse: true`, `file_type: file`).
   - When matching certificates are found:
     - Ensure `{{ devenv_home }}/.config/node` exists (`mode: "0755"`).
     - Read certificate contents (`slurp`).
     - Fold them idempotently (via `ansible.builtin.blockinfile`, `create: true`, `mode: "0644"`) into a single combined
       PEM bundle at `{{ devenv_home }}/.config/node/node-extra-ca.pem`.

2. **Export `NODE_EXTRA_CA_CERTS` Across All Managed Shells**:
   - In `dotfiles/fish/.config/fish/conf.d/00-devenv.fish`, `dotfiles/bash/.bashrc`, `dotfiles/zsh/.zshrc`, and
     `dotfiles/examples/devenv-shell-snippets.sh`:
     - Export `NODE_EXTRA_CA_CERTS` pointing to `$HOME/.config/node/node-extra-ca.pem` whenever that file exists
       (`if test -f "$HOME/.config/node/node-extra-ca.pem"` in Fish; `if [ -f "$HOME/.config/node/node-extra-ca.pem" ]`
       in Bash/Zsh/snippets).

3. **Tests & Verification (`tests/test_toolchain.py`)**:
   - Add unit tests in `tests/test_toolchain.py` verifying the Ansible `node` role tasks (`ca-certificates`,
     `node-extra-ca.pem`) and multi-shell `NODE_EXTRA_CA_CERTS` configuration.
   - Run `uv run --extra test pytest -m "not network"`, `uv run ruff check .`,
     `uv run --extra test ansible-lint ansible/site.yml`, `npx prettier --check "**/*.md"`, and `make check`.

## Resolution

- Implemented via Holon flow `node-extra-ca` (Bean 0332).
- Pull Request #29: [https://github.com/thomashan/dev-env/pull/29](https://github.com/thomashan/dev-env/pull/29) merged
  to `main` (`4aeb1c2`) on 2026-11-19.
