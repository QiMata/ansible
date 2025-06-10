import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    assert host.package('vault').is_installed


def test_service_running(host):
    svc = host.service('vault')
    assert svc.is_enabled
    assert svc.is_running


def test_config_file(host):
    cfg = host.file('/etc/vault/vault.hcl')
    assert cfg.exists
    assert cfg.contains('listener "tcp"')


def test_port(host):
    assert host.socket('tcp://0.0.0.0:8200').is_listening

