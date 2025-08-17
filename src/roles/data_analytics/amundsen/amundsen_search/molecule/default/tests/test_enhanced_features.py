import os
import testinfra.utils.ansible_runner
import pytest


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_auth_config_files_when_enabled(host):
    """Test authentication configuration files when auth is enabled"""
    # Check if auth is enabled in config
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    if cfg.contains('AUTH_ENABLED = True'):
        # Check for API keys file
        if cfg.contains('api_key'):
            api_keys = host.file('/etc/amundsen/search/api_keys.yml')
            assert api_keys.exists
            assert api_keys.user == 'amundsen'
            assert api_keys.mode == 0o600
        
        # Check for JWT secret file
        if cfg.contains('jwt'):
            jwt_secret = host.file('/etc/amundsen/search/jwt_secret.yml')
            assert jwt_secret.exists
            assert jwt_secret.user == 'amundsen'
            assert jwt_secret.mode == 0o600


def test_elasticsearch_credentials_when_enabled(host):
    """Test Elasticsearch credentials file when ES auth is enabled"""
    es_creds = host.file('/etc/amundsen/search/es_credentials.yml')
    if es_creds.exists:
        assert es_creds.user == 'amundsen'
        assert es_creds.mode == 0o600


def test_tls_certificates_when_enabled(host):
    """Test TLS certificate files when TLS is enabled"""
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    if cfg.contains('TLS_ENABLED = True'):
        cert_dir = host.file('/opt/amundsen/search/certs')
        assert cert_dir.is_directory
        assert cert_dir.user == 'amundsen'
        assert cert_dir.mode == 0o700


def test_health_check_timer_when_enabled(host):
    """Test health check timer when health checks are enabled"""
    timer = host.file('/etc/systemd/system/amundsen-search-health.timer')
    if timer.exists:
        assert timer.contains('OnUnitActiveSec=')
        service = host.file('/etc/systemd/system/amundsen-search-health.service')
        assert service.exists
        assert service.contains('health_check.py')


def test_metrics_service_when_enabled(host):
    """Test metrics service when monitoring is enabled"""
    metrics_service = host.file('/etc/systemd/system/amundsen-search-metrics.service')
    if metrics_service.exists:
        assert metrics_service.contains('prometheus_metrics.py')
        assert metrics_service.contains('User=amundsen')


def test_backup_scripts_when_enabled(host):
    """Test backup scripts when backup is enabled"""
    backup_script = host.file('/opt/amundsen/search/venv/backup.py')
    if backup_script.exists:
        assert backup_script.mode == 0o755
        assert backup_script.user == 'amundsen'
        
        restore_script = host.file('/opt/amundsen/search/venv/restore.py')
        assert restore_script.exists
        assert restore_script.mode == 0o755


def test_curator_config_when_enabled(host):
    """Test curator configuration when index management is enabled"""
    curator_config = host.file('/etc/amundsen/search/curator.yml')
    if curator_config.exists:
        assert curator_config.user == 'amundsen'
        assert curator_config.contains('client:')
        
        curator_actions = host.file('/etc/amundsen/search/curator_actions.yml')
        assert curator_actions.exists
        assert curator_actions.contains('actions:')


def test_environment_specific_configs(host):
    """Test environment-specific configuration files"""
    dev_config = host.file('/opt/amundsen/search/venv/development_config.py')
    staging_config = host.file('/opt/amundsen/search/venv/staging_config.py')
    
    # If either exists, they should be properly configured
    if dev_config.exists:
        assert dev_config.contains('DevelopmentConfig')
        assert dev_config.user == 'amundsen'
    
    if staging_config.exists:
        assert staging_config.contains('StagingConfig')
        assert staging_config.user == 'amundsen'


def test_multi_instance_support(host):
    """Test multi-instance deployment support"""
    # Check if multi-instance systemd units exist
    service_files = host.run("ls /etc/systemd/system/amundsen-search*.service").stdout
    
    # Should have at least the main service
    assert 'amundsen-search.service' in service_files or 'amundsen-search-' in service_files


def test_security_hardening(host):
    """Test security hardening in systemd service"""
    unit = host.file('/etc/systemd/system/amundsen-search.service')
    assert unit.contains('NoNewPrivileges=true')
    assert unit.contains('PrivateTmp=true')
    assert unit.contains('ProtectSystem=strict')
    assert unit.contains('ProtectHome=true')


def test_logging_configuration(host):
    """Test logging configuration"""
    # Check if structured logging is configured
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    if cfg.contains('LOG_FORMAT'):
        # Should have either json or standard format
        assert cfg.contains('"json"') or cfg.contains('"standard"')
    
    # Check if log rotation is configured
    logrotate = host.file('/etc/logrotate.d/amundsen-search')
    if logrotate.exists:
        assert logrotate.contains('daily')
        assert logrotate.contains('compress')


@pytest.mark.parametrize("config_var", [
    "ELASTICSEARCH_ENDPOINT",
    "SEARCH_RESULT_SIZE", 
    "LOG_LEVEL",
    "GRACEFUL_TIMEOUT"
])
def test_essential_config_variables(host, config_var):
    """Test that essential configuration variables are present"""
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    assert cfg.contains(config_var)
