import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_repo_cloned(host):
    d = host.file('/opt/myapp')
    assert d.is_directory


def test_service_file(host):
    f = host.file('/etc/systemd/system/myapp.service')
    assert f.exists


def test_service_running(host):
    s = host.service('myapp')
    assert s.is_enabled
