import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_service_running(host):
    svc = host.service('slapd')
    assert svc.is_enabled
    assert svc.is_running

def test_domain_suffix(host):
    cmd = host.run('ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcSuffix')
    assert 'dc=example,dc=com' in cmd.stdout

def test_log_level(host):
    cmd = host.run('ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcLogLevel')
    assert '256' in cmd.stdout
