import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_no_upgrades(host):
    cmd = host.run('apt list --upgradeable')
    assert 'upgradable from' not in cmd.stdout

