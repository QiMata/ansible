from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scripts.create_ansible_inventory import ContainerRecord, generate_inventory


def test_container_record_normalization():
    row = (
        "Prod Env",
        "Application-Category",
        "System One",
        "host-01",
        "10.0.0.1/24",
        "10.0.0.2",
        "mariadb_database",
    )
    record = ContainerRecord.from_row(row)

    assert record.environment == "Prod_Env"
    assert record.category == "Application_Category"
    assert record.system == "System_One"
    assert record.container == "host_01"
    assert record.management_ip == "10.0.0.1"
    assert record.service_ip == "10.0.0.2"
    assert record.application == "mariadb_database"


def test_generate_inventory_creates_expected_ini(tmp_path: Path):
    rows = [
        (
            "Prod",
            "Category A",
            "SystemX",
            "Host01",
            "192.168.1.10/24",
            "10.1.0.5/32",
            "app",
        ),
        (
            "Prod",
            "Category A",
            "SystemX",
            "Host02",
            "192.168.1.11",
            "10.1.0.6",
            "MARIADB_DATABASE",
        ),
        (
            "Prod",
            "Category B",
            "SystemY",
            "Host03",
            "192.168.2.10",
            "10.2.0.5",
            "app2",
        ),
    ]

    generate_inventory(rows, tmp_path, ansible_user="deploy", become_pass="complex pass")

    inventory_path = tmp_path / "Prod.ini"
    assert inventory_path.exists()

    content = inventory_path.read_text().splitlines()

    assert content[:3] == ["[all:children]", "Category_A", "Category_B"]
    assert "[Category_A:children]" in content
    assert "[SystemX:children]" in content
    assert "SystemX_MARIADB_DATABASE" in content
    assert "SystemX_app" in content

    mariadb_line = next(line for line in content if line.startswith("Host02 ansible_host"))
    assert "galera_cluster_bind_address=10.1.0.6" in mariadb_line
    assert "ansible_user=deploy" in mariadb_line
    assert "ansible_become_pass='complex pass'" in mariadb_line

    redis_line = next(line for line in content if line.startswith("Host01 ansible_host"))
    assert "ansible_user=deploy" in redis_line
    assert "ansible_become_pass='complex pass'" in redis_line


def test_generate_inventory_raises_on_invalid_ip(tmp_path: Path):
    rows = [
        ("Prod", "Category", "System", "Host", "", "10.0.0.2", "app"),
    ]

    with pytest.raises(ValueError):
        generate_inventory(rows, tmp_path)
