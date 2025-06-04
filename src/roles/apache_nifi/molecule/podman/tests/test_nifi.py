import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_java_installed(host):
    cmd = host.run('java -version')
    assert cmd.rc == 0


def test_nifi_user(host):
    assert host.user('nifi').exists


def test_install_dir(host):
    nifi_dir = host.file('/opt/nifi')
    assert nifi_dir.is_directory


def test_config_files(host):
    assert host.file('/opt/nifi/conf/nifi.properties').exists
    assert host.file('/opt/nifi/conf/bootstrap.conf').exists


def test_service_running(host):
    svc = host.service('nifi')
    assert svc.is_enabled
    assert svc.is_running
    assert host.socket('tcp://0.0.0.0:9443').is_listening
