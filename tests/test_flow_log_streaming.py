"""The wrapper's output reaches a redirected log as it happens, not when the process exits (bean 0385)."""

import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/holon_flow/scripts"

DRIVER = """
import sys
sys.path.insert(0, {scripts!r})
import run_holon_flow as r
r.enable_line_buffering()
r.log_info("wrapper line")
code, _ = r.execute_flow_process(
    [sys.executable, "-c", "import time; print('STAGE 1 intent', flush=True); time.sleep(30)"]
)
"""


def test_wrapper_and_child_lines_reach_redirected_log_before_exit(tmp_path):
    log = tmp_path / "flow.log"
    with log.open("w") as out:
        proc = subprocess.Popen(
            [sys.executable, "-c", DRIVER.format(scripts=str(SCRIPTS))], stdout=out, stderr=subprocess.STDOUT
        )
        try:
            deadline = time.time() + 20
            text = ""
            while time.time() < deadline:
                text = log.read_text()
                if "STAGE 1 intent" in text:
                    break
                time.sleep(0.1)
            assert proc.poll() is None, "driver exited early"
            assert "wrapper line" in text
            assert "STAGE 1 intent" in text
        finally:
            proc.kill()
            proc.wait()
