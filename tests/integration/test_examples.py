import os
import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def _run(script: str) -> str:
    result = subprocess.run(
        [sys.executable, script],
        cwd=EXAMPLES_DIR,
        env={**os.environ},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_basic_example():
    output = _run("basic.py")
    assert "Jobs:" in output


def test_async_basic_example():
    output = _run("async_basic.py")
    assert "Jobs:" in output
