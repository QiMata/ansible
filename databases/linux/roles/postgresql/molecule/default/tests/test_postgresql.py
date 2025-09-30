import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_service_running(host):
    service = host.service('postgresql')
    assert service.is_running
    assert service.is_enabled


def test_port_listening(host):
    assert host.socket('tcp://0.0.0.0:5432').is_listening


def test_config(host):
    cfg = host.file('/etc/postgresql/15/main/postgresql.conf')
    assert cfg.exists
    assert 'scram-sha-256' in cfg.content_string
