import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_packages_installed(host):
    assert host.package('step-ca').is_installed
    assert host.package('step').is_installed


def test_user(host):
    u = host.user('step')
    assert u.exists


def test_config_file(host):
    f = host.file('/home/step/.step/config/ca.json')
    assert f.exists
    assert f.user == 'step'


def test_service(host):
    svc = host.service('step-ca')
    assert svc.is_enabled
    assert svc.is_running


def test_port(host):
    assert host.socket('tcp://0.0.0.0:8443').is_listening

