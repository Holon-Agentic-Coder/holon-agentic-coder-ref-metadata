---
id: "0325"
title: "Support corporate proxy SSL certificates for Ansible Galaxy and Conda via system CA trust store"
status: todo
created_at: 2026-11-18T11:31:00+11:00
updated_at: 2026-11-18T11:31:00+11:00
tags:
  - dev-env
  - ssl
  - proxy
  - corporate-network
  - ansible-galaxy
  - conda
  - makefile
  - bugfix
---

# 0325 - Support corporate proxy SSL certificates for Ansible Galaxy and Conda via system CA trust store

## Problem Statement

When running `make bootstrap` or `make install` on corporate machines behind an SSL-intercepting proxy (e.g. Ubuntu with
internal corporate root CAs installed in `/etc/ssl/certs/ca-certificates.crt`), network calls initiated by Python tools
fail with:

```text
[WARNING]: Skipping Galaxy server https://galaxy.ansible.com. Got an unexpected error when getting available versions of collection community.general: Unknown error when attempting to call Galaxy at 'https://galaxy.ansible.com/api/': <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1035)>
[ERROR]: Unknown error when attempting to call Galaxy at 'https://galaxy.ansible.com/api/': <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1035)>
<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1035)>
make[1]: *** [Makefile:156: bootstrap] Error 1
```

### Root Cause

1. **Isolated Conda CA Bundle**: Python installed inside Conda/Micromamba uses `certifi` and its compiled OpenSSL
   default bundle (`<prefix>/ssl/cacert.pem`). This bundle only contains standard public Mozilla root certificates and
   does not inherit the host's system trust store where corporate root CAs reside.
2. **Missing `SSL_CERT_FILE` Propagation**: Python's `ssl` module (`urllib.request`) and Python `requests` respect
   `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE`. When these variables are unset, Python fails to verify certificates issued
   by the corporate proxy.
3. **Conda SSL Verification**: Conda similarly fails to verify package repositories unless `ssl_verify` in `.condarc`
   points to the host's CA bundle.

## Scope of Changes

1. **Auto-Detect System CA Trust Bundle in `Makefile` (`Makefile`)**:
   - Probe for host CA bundle paths:
     - Debian/Ubuntu: `/etc/ssl/certs/ca-certificates.crt`
     - RHEL/CentOS/Fedora: `/etc/pki/tls/certs/ca-bundle.crt`
     - macOS: `/etc/ssl/cert.pem`
   - If detected, export `SSL_CERT_FILE ?= $(SYSTEM_CA_BUNDLE)`, `REQUESTS_CA_BUNDLE ?= $(SYSTEM_CA_BUNDLE)`, and
     `CURL_CA_BUNDLE ?= $(SYSTEM_CA_BUNDLE)` in `Makefile` so all sub-processes (Python, Ansible Galaxy, Conda)
     automatically trust corporate proxy certificates.

2. **Ansible Galaxy CA & Insecure Fallback (`Makefile`, `ansible.cfg`)**:
   - In `Makefile`, allow passing `--ignore-certs` to `ansible-galaxy collection install` when
     `DEVENV_INSECURE_SSL=true` or automatically fall back if an SSL certificate verify failure occurs.
   - In `ansible.cfg`, support `ca_cert` under `[galaxy]` pointing to the detected system CA bundle.

3. **Preserve Corporate CA in `.condarc` (`scripts/devenv_wizard.py`)**:
   - When the configuration wizard writes `.condarc`, preserve or inject `ssl_verify` if a system CA bundle is present
     on the host.

4. **Tests & Verification**:
   - Add tests in `tests/test_toolchain.py` verifying that `Makefile` detects system CA bundles and propagates
     `SSL_CERT_FILE`.
   - Run `make test`, `make lint`, and `make check`.
