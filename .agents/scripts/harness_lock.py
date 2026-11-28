#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

LOCK_NAME = "harness-commit.lock"
LOCK_TIMEOUT_SECONDS = 300
POLL_SECONDS = 0.2


class HarnessLockTimeout(RuntimeError):
    pass


def lock_path(repo):
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return Path(common) / LOCK_NAME


@contextmanager
def exclusive_harness_lock(repo, timeout=LOCK_TIMEOUT_SECONDS):
    with open(lock_path(repo), "a") as handle:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise HarnessLockTimeout(f"could not take {LOCK_NAME} within {timeout}s") from None
                time.sleep(POLL_SECONDS)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
