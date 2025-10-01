import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_service_running(host):
    svc = host.service('netbox')
    assert svc.is_enabled
    assert svc.is_running
    assert host.socket('tcp://0.0.0.0:8000').is_listening

def test_config(host):
    cfg = host.file('/opt/netbox/netbox/netbox/configuration.py')
    assert cfg.exists
    assert 'ALLOWED_HOSTS' in cfg.content_string

def test_static_files(host):
    static = host.file('/opt/netbox/netbox/static')
    assert static.is_directory
