import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    pkg = host.package('grafana')
    assert pkg.is_installed


def test_service_running(host):
    service = host.service('grafana-server')
    assert service.is_enabled
    assert service.is_running


def test_config_file(host):
    cfg = host.file('/etc/grafana/grafana.ini')
    assert cfg.exists
    assert cfg.user == 'root'


def test_port_listening(host):
    assert host.socket('tcp://0.0.0.0:3000').is_listening
