import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    assert host.package('haproxy').is_installed


def test_service_running(host):
    service = host.service('haproxy')
    assert service.is_enabled
    assert service.is_running


def test_config_file(host):
    cfg = host.file('/etc/haproxy/haproxy.cfg')
    assert cfg.exists
    assert cfg.contains('frontend http_frontend')
    assert cfg.contains('backend http_backend')


def test_error_files(host):
    for code in ['400','403','408','500','502','503','504']:
        f = host.file(f'/etc/haproxy/errors/{code}.http')
        assert f.exists
        assert oct(f.mode) == '0o644'


def test_port_listening(host):
    assert host.socket('tcp://0.0.0.0:80').is_listening
