import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    assert host.package('jenkins').is_installed


def test_service_running(host):
    service = host.service('jenkins')
    assert service.is_enabled
    assert service.is_running


def test_port_listening(host):
    assert host.socket('tcp://0.0.0.0:8080').is_listening


def test_init_groovy(host):
    f = host.file('/var/lib/jenkins/init.groovy.d/init_admin_user.groovy')
    assert f.exists
    assert f.user == 'jenkins'
    assert oct(f.mode) == '0o644'
