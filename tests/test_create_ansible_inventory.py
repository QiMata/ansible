from pathlib import Path
import shlex
import sys
import types

# Ensure the scripts directory is importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "src" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Provide a lightweight psycopg2 stub so the module under test can be imported
if "psycopg2" not in sys.modules:
    psycopg2_stub = types.ModuleType("psycopg2")
    psycopg2_stub.connect = lambda *args, **kwargs: None
    sys.modules["psycopg2"] = psycopg2_stub

from create_ansible_inventory import create_ansible_inventory_server_string


def test_inventory_includes_become_pass_with_safe_quoting():
    become_pass = "S3cr3t Pass!"
    result = create_ansible_inventory_server_string(
        env="dev",
        cat="app",
        ss="server",
        app="web",
        cont="container01",
        management_ip="10.0.0.1/24",
        service_ip="10.0.1.1/24",
        ansible_user="ubuntu",
        become_pass=become_pass,
    )

    quoted_pass = shlex.quote(become_pass)
    assert f"ansible_become_pass={quoted_pass}" in result
    assert "ansible_user=ubuntu" in result


def test_inventory_omits_become_pass_when_not_provided():
    result = create_ansible_inventory_server_string(
        env="dev",
        cat="app",
        ss="server",
        app="web",
        cont="container01",
        management_ip="10.0.0.1/24",
        service_ip="10.0.1.1/24",
    )

    assert "ansible_become_pass" not in result
