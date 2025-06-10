import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_client_installed(host):
    assert host.package('postgresql-client').is_installed


def test_database_created(host):
    cmd = host.run("psql -U postgres -tAc 'SELECT 1 FROM pg_database WHERE datname=\'keycloak\''")
    assert cmd.rc == 0
    assert '1' in cmd.stdout


def test_user_created(host):
    cmd = host.run("psql -U postgres -tAc 'SELECT 1 FROM pg_roles WHERE rolname=\'keycloak\''")
    assert cmd.rc == 0
    assert '1' in cmd.stdout
