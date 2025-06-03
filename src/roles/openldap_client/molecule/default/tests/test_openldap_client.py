import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_packages(host):
    for pkg in ['sssd', 'libpam-sss', 'libnss-sss', 'krb5-user']:
        assert host.package(pkg).is_installed

def test_sssd_conf(host):
    cfg = host.file('/etc/sssd/sssd.conf')
    assert cfg.exists
    assert cfg.mode == 0o600

def test_service_running(host):
    svc = host.service('sssd')
    assert svc.is_enabled
    assert svc.is_running
