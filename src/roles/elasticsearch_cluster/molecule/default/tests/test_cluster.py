import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_config_file(host):
    cfg = host.file('/etc/elasticsearch/elasticsearch.yml')
    assert cfg.exists
    assert 'cluster.name' in cfg.content_string

def test_heap_file(host):
    heap = host.file('/etc/elasticsearch/jvm.options.d/heap_size.options')
    assert heap.exists
    assert '-Xms' in heap.content_string

def test_service_running(host):
    svc = host.service('elasticsearch')
    assert svc.is_enabled
    assert svc.is_running
    assert host.socket('tcp://0.0.0.0:9200').is_listening
