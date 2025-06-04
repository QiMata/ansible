import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_packages_installed(host):
    assert host.package('apt-mirror').is_installed
    assert host.package('apache2').is_installed


def test_base_dir(host):
    d = host.file('/var/spool/apt-mirror')
    assert d.is_directory


def test_config_file(host):
    cfg = host.file('/etc/apt/mirror.list')
    assert cfg.exists


def test_apache_service(host):
    svc = host.service('apache2')
    assert svc.is_enabled
    assert svc.is_running
