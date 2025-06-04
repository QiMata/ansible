import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_rsyslog_config(host):
    cfg = host.file('/etc/rsyslog.d/50-ldap.conf')
    assert cfg.exists
    assert 'local4.*' in cfg.content_string

def test_log_file(host):
    log = host.file('/var/log/ldap.log')
    assert log.exists

def test_filebeat_running(host):
    assert host.package('filebeat').is_installed
    svc = host.service('filebeat')
    assert svc.is_enabled
    assert svc.is_running
