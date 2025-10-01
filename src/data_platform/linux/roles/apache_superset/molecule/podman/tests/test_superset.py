import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_venv_exists(host):
    venv = host.file('/opt/superset/venv')
    assert venv.is_directory


def test_apache_superset_cli(host):
    cmd = host.run('/opt/superset/venv/bin/superset --version')
    assert cmd.rc == 0


def test_config_file(host):
    cfg = host.file('/etc/superset/apache_superset_config.py')
    assert cfg.exists


def test_service_running(host):
    svc = host.service('superset')
    assert svc.is_enabled
    assert svc.is_running
    sock = host.socket('tcp://0.0.0.0:8088')
    assert sock.is_listening
