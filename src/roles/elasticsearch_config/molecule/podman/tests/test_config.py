import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_elasticsearch_yml(host):
    cfg = host.file('/etc/elasticsearch/elasticsearch.yml')
    assert cfg.exists
    assert 'cluster.name' in cfg.content_string

def test_heap_file(host):
    heap = host.file('/etc/elasticsearch/jvm.options.d/heap.options')
    assert heap.exists
    assert '-Xms' in heap.content_string
    assert '-Xmx' in heap.content_string
