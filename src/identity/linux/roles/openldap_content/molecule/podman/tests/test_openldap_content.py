import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_base_entry(host):
    cmd = host.run("ldapsearch -x -LLL -b 'dc=example,dc=com' -s base dn")
    assert 'dc=example,dc=com' in cmd.stdout

def test_people_ou(host):
    cmd = host.run("ldapsearch -x -LLL -b 'ou=eng,dc=example,dc=com' dn")
    assert 'ou=eng,dc=example,dc=com' in cmd.stdout
