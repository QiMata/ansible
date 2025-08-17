import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_service_running(host):
    svc = host.service('slapd')
    assert svc.is_enabled
    assert svc.is_running

def test_basedn(host):
    cmd = host.run('ldapsearch -x -LLL -H ldapi:/// -b cn=config olcSuffix')
    assert 'dc=example,dc=com' in cmd.stdout

def test_rootdn(host):
    cmd = host.run('ldapsearch -x -LLL -H ldapi:/// -b cn=config olcRootDN')
    assert 'cn=Manager,dc=example,dc=com' in cmd.stdout
