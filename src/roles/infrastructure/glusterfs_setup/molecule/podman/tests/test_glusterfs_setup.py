import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    pkg = host.package('glusterfs-server')
    assert pkg.is_installed


def test_service_running(host):
    service = host.service('glusterfs-server')
    assert service.is_enabled
    assert service.is_running


def test_brick_directory(host):
    d = host.file('/glusterfs/brick1/gv0')
    assert d.is_directory
    assert d.user == 'root'
    assert d.group == 'root'
    assert oct(d.mode) == '0o755'


def test_port_listening(host):
    assert host.socket('tcp://0.0.0.0:24007').is_listening
