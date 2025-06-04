import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_filebeat_package(host):
    pkg = host.package('filebeat')
    assert pkg.is_installed

def test_config_file(host):
    cfg = host.file('/etc/filebeat/filebeat.yml')
    assert cfg.exists
    assert 'filebeat.inputs' in cfg.content_string

def test_service_running(host):
    svc = host.service('filebeat')
    assert svc.is_enabled
    assert svc.is_running
