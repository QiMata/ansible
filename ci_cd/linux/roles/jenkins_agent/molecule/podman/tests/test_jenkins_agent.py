import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_user_exists(host):
    user = host.user('jenkins')
    assert user.exists
    assert user.shell == '/bin/bash'


def test_java_installed(host):
    assert host.package('openjdk-11-jdk').is_installed


def test_authorized_key(host):
    f = host.file('/home/jenkins/.ssh/authorized_keys')
    assert f.exists
    assert f.user == 'jenkins'
    assert f.mode == 0o600
