import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    assert host.package('openssh-server').is_installed


def test_service_running(host):
    svc = host.service('sshd')
    assert svc.is_enabled
    assert svc.is_running


def test_port_listening(host):
    assert host.socket('tcp://0.0.0.0:22').is_listening


def test_config(host):
    cfg = host.file('/etc/ssh/sshd_config')
    assert cfg.contains('PermitRootLogin no')
    assert cfg.contains('PasswordAuthentication')

