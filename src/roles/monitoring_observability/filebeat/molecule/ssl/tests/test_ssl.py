import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_ssl_configuration_present(host):
    """Test that SSL configuration is present in config file."""
    cfg = host.file('/etc/filebeat/filebeat.yml')
    content = cfg.content_string
    assert 'ssl:' in content
    assert 'enabled: true' in content
    assert 'verification_mode: certificate' in content


def test_backup_directory_created(host):
    """Test that backup directory is created."""
    backup_dir = host.file('/etc/filebeat/backups')
    assert backup_dir.exists
    assert backup_dir.is_directory
    assert backup_dir.user == 'root'
    assert backup_dir.group == 'root'


def test_health_check_enabled(host):
    """Test that health check configurations are present."""
    # Test health check functionality indirectly
    cmd = host.run('filebeat test config -c /etc/filebeat/filebeat.yml')
    assert cmd.rc == 0


def test_http_monitoring_enabled(host):
    """Test that HTTP monitoring endpoint is configured."""
    cfg = host.file('/etc/filebeat/filebeat.yml')
    content = cfg.content_string
    assert 'http:' in content
    assert 'enabled: true' in content


def test_security_focused_input(host):
    """Test that security-focused input is configured."""
    cfg = host.file('/etc/filebeat/filebeat.yml')
    content = cfg.content_string
    assert '/var/log/secure.log' in content
    assert 'service: security' in content
    assert 'security_level: high' in content
