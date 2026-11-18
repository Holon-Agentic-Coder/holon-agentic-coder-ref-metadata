---
id: "0326"
title:
  "Automatically inject custom CA certificates into Miniforge cacert.pem during make bootstrap and Ansible convergence"
status: in-progress
created_at: 2026-11-18T11:51:00+11:00
updated_at: 2026-11-18T11:51:00+11:00
tags:
  - dev-env
  - ssl
  - proxy
  - corporate-ca
  - makefile
  - ansible
  - bugfix
---

# 0326 - Automatically inject custom CA certificates into Miniforge cacert.pem during make bootstrap and Ansible convergence

## Problem Statement

On corporate-managed machines (such as those using Netskope or Zscaler SSL inspection), enterprise root and tenant
certificates are installed into `/usr/local/share/ca-certificates/` (e.g. `nscacert.crt`, `nstenantcert.crt`).

While Ubuntu system tools trust these certificates via `/etc/ssl/certs/ca-certificates.crt`, Conda and Miniforge
maintain their own internal OpenSSL certificate bundle at `$(CONDA_DIR)/ssl/cacert.pem` (and `cert.pem`).

When sub-processes, pip, Conda, or Python network scripts run without an explicit `SSL_CERT_FILE` override, they rely on
`cacert.pem` and fail with SSL certificate verification errors.

To guarantee seamless operation, both `make bootstrap` (prior to Ansible execution) and the Ansible `conda` role (during
convergence) must automatically detect custom certificates in `/usr/local/share/ca-certificates/` and append them to
`$(CONDA_DIR)/ssl/cacert.pem` if they are not already present.

## Scope of Changes

1. **Pre-Ansible Auto-Injection in `Makefile` (`Makefile`)**:
   - In the `bootstrap` target, before calling `ansible-galaxy collection install` or `conda install`:
     - Check if `/usr/local/share/ca-certificates` exists and `$(CONDA_DIR)/ssl/cacert.pem` exists.
     - For each `.crt` or `.pem` in `/usr/local/share/ca-certificates/`:
       - Extract the certificate body or header pattern.
       - Check if it is already present in `$(CONDA_DIR)/ssl/cacert.pem`.
       - If absent, append it cleanly with a `# Custom CA: <filename>` comment header.

2. **Idempotent CA Sync in Ansible Conda Role (`ansible/roles/conda/tasks/main.yml`)**:
   - In Ansible's `conda` role, add idempotent tasks that:
     - Scan `/usr/local/share/ca-certificates` for `.crt` and `.pem` files on Debian/Ubuntu hosts.
     - Ensure each certificate is injected into `{{ devenv_conda_root }}/ssl/cacert.pem` if not already present.

3. **Tests & Verification (`tests/test_toolchain.py`)**:
   - Add unit tests verifying:
     - The `Makefile` bootstrap recipe contains the CA certificate injection logic.
     - The injection is idempotent (does not duplicate certificates).
   - Run `make test`, `make lint`, and `make check`.
