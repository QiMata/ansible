import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_service_running(host):
    svc = host.service('neo4j')
    assert svc.is_enabled
    assert svc.is_running
    assert host.socket('tcp://0.0.0.0:7687').is_listening

def test_config(host):
    cfg = host.file('/etc/neo4j/neo4j.conf')
    assert cfg.exists
    assert 'dbms.default_listen_address' in cfg.content_string

def test_neo4j_user(host):
    assert host.user('neo4j').exists
    data_dir = host.file('/var/lib/neo4j/data')
    assert data_dir.is_directory
    assert data_dir.user == 'neo4j'
