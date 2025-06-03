import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_telnet_removed(host):
    assert not host.package('telnet').is_installed


def test_ftp_removed(host):
    assert not host.package('ftp').is_installed
