import os
import subprocess
import venv
from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).parent.parent.parent / "examples" / "example"


@pytest.fixture(scope="module")
def venv_python(tmp_path_factory):
    """Fresh venv with very-good-ffmpeg installed from PyPI via requirements.txt."""
    venv_dir = tmp_path_factory.mktemp("venv")
    venv.create(str(venv_dir), with_pip=True)
    python = venv_dir / "bin" / "python"
    subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(EXAMPLE_DIR / "requirements.txt"), "--quiet"],
        check=True,
    )
    return python


def test_example_src(venv_python):
    result = subprocess.run(
        [str(venv_python), "main.py"],
        cwd=EXAMPLE_DIR,
        env={**os.environ},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Jobs (sync):" in result.stdout
    assert "Jobs (async):" in result.stdout
