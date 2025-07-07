import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    assert host.package('ufw').is_installed


def test_service_running(host):
    svc = host.service('ufw')
    assert svc.is_enabled
    assert svc.is_running


def test_status(host):
    cmd = host.run('ufw status')
    assert 'Status: active' in cmd.stdout
    assert '22/tcp' in cmd.stdout

