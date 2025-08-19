import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_elasticsearch_output_configuration(host):
    """Test that Elasticsearch output is configured correctly."""
    cfg = host.file('/etc/filebeat/filebeat.yml')
    content = cfg.content_string
    assert 'output.elasticsearch:' in content
    assert 'elasticsearch.test.local:9200' in content
    assert 'test-filebeat-' in content


def test_filebeat_service_running(host):
    """Test that Filebeat service is running."""
    svc = host.service('filebeat')
    assert svc.is_running
    assert svc.is_enabled


def test_config_validation_elasticsearch(host):
    """Test that configuration is valid for Elasticsearch output."""
    cmd = host.run('filebeat test config -c /etc/filebeat/filebeat.yml')
    assert cmd.rc == 0
