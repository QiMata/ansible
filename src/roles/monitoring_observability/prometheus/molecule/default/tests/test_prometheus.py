import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_prometheus_service(host):
    service = host.service('prometheus')
    assert service.is_running
    assert service.is_enabled


def test_node_exporter_service(host):
    service = host.service('prometheus-node-exporter')
    assert service.is_running
    assert service.is_enabled


def test_config_file(host):
    cfg = host.file('/etc/prometheus/prometheus.yml')
    assert cfg.exists
    assert 'scrape_interval' in cfg.content_string
