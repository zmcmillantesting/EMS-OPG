import subprocess
import sys
from pathlib import Path


def test_init_db_script_runs_from_project_root():
    root = Path(__file__).resolve().parents[2]
    script = root / "src" / "ems_opg" / "database" / "init_db.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
