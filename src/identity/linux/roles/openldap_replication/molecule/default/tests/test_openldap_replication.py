import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_syncrepl_config(host):
    cmd = host.run('ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcSyncrepl')
    assert 'olcSyncrepl' in cmd.stdout

def test_serverid(host):
    cmd = host.run('ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config olcServerID')
    assert 'olcServerID' in cmd.stdout
