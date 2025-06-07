import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_user_exists(host):
    user = host.user('nexus')
    assert user.exists


def test_service_running(host):
    svc = host.service('nexus')
    assert svc.is_enabled
    assert svc.is_running
