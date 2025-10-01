import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_cert_directory(host):
    d = host.file('/etc/elasticsearch/certs')
    assert d.is_directory
    assert d.user == 'root'
    assert d.group == 'elasticsearch'

def test_role_mapping(host):
    mapping = host.file('/etc/elasticsearch/role_mapping.yml')
    assert mapping.exists
