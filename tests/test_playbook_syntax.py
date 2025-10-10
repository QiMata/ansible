import pathlib
import subprocess

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAYBOOK_DIR = PROJECT_ROOT / "src" / "playbooks"
INVENTORY = PROJECT_ROOT / "tests" / "fixtures" / "minimal_inventory.ini"

PLAYBOOK_NAMES = [
    "minio.yml",
    "spark.yml",
    "grafana.yml",
    "prometheus.yml",
]


@pytest.mark.parametrize("playbook_name", PLAYBOOK_NAMES)
def test_playbook_syntax(playbook_name: str) -> None:
    playbook_path = PLAYBOOK_DIR / playbook_name
    assert playbook_path.exists(), f"Playbook {playbook_name} is missing"

    cmd = [
        "ansible-playbook",
        "-i",
        str(INVENTORY),
        "--syntax-check",
        str(playbook_path),
    ]

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT / "src"),
        check=False,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"ansible-playbook syntax-check failed for {playbook_name}:\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
