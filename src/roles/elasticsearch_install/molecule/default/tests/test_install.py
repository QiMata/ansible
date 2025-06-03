import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_repo_file(host):
    f = host.file('/etc/apt/sources.list.d/elasticsearch.list')
    assert f.exists
    assert 'artifacts.elastic.co' in f.content_string

def test_package_installed(host):
    pkg = host.package('elasticsearch')
    assert pkg.is_installed

def test_service_enabled(host):
    svc = host.service('elasticsearch')
    assert svc.is_enabled
