import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_virtualenv_exists(host):
    venv = host.file('/opt/amundsen/search/venv')
    assert venv.is_directory


def test_package_installed(host):
    cmd = host.run('/opt/amundsen/search/venv/bin/pip show amundsen-search')
    assert cmd.rc == 0


def test_config_file(host):
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    assert cfg.exists
    assert cfg.contains('ELASTICSEARCH_ENDPOINT')


def test_systemd_unit(host):
    unit = host.file('/etc/systemd/system/amundsen-search.service')
    assert unit.exists
    assert unit.contains('--bind 0.0.0.0:5001')


def test_service_running(host):
    svc = host.service('amundsen-search')
    assert svc.is_enabled
    assert svc.is_running
    sock = host.socket('tcp://0.0.0.0:5001')
    assert sock.is_listening
