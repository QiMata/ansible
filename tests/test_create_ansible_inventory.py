import pathlib
import shlex
import sys
import types

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if 'psycopg2' not in sys.modules:
    sys.modules['psycopg2'] = types.ModuleType('psycopg2')

from src.scripts.create_ansible_inventory import create_ansible_inventory_server_string


def test_create_ansible_inventory_server_string_includes_become_pass():
    inventory = create_ansible_inventory_server_string(
        env="prod",
        cat="web",
        ss="frontend",
        app="app",
        cont="host1",
        management_ip="10.0.0.1/24",
        service_ip="10.0.1.1/24",
        ansible_user="ansible",
        become_pass="pa ss$word",
    )

    expected_fragment = f"ansible_become_pass={shlex.quote('pa ss$word')}"
    assert expected_fragment in inventory
