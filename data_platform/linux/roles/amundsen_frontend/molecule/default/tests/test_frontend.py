import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_virtualenv_exists(host):
    venv = host.file('/opt/amundsen/frontend/venv')
    assert venv.is_directory


def test_package_installed(host):
    cmd = host.run('/opt/amundsen/frontend/venv/bin/pip show amundsen-frontend')
    assert cmd.rc == 0


def test_config_file(host):
    cfg = host.file('/opt/amundsen/frontend/venv/config.py')
    assert cfg.exists
    assert cfg.contains('SEARCHSERVICE_BASE')
    assert cfg.contains('METADATASERVICE_BASE')


def test_systemd_unit(host):
    unit = host.file('/etc/systemd/system/amundsen-frontend.service')
    assert unit.exists
    assert unit.contains('--bind 0.0.0.0:5000')


def test_service_running(host):
    svc = host.service('amundsen-frontend')
    assert svc.is_enabled
    assert svc.is_running
    sock = host.socket('tcp://0.0.0.0:5000')
    assert sock.is_listening
