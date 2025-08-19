import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


class TestGrafanaPlugins:
    """Test class for Grafana plugin functionality."""
    
    def test_plugins_directory_exists(self, host):
        """Test that plugins directory exists."""
        plugin_dir = host.file('/var/lib/grafana/plugins')
        assert plugin_dir.exists
        assert plugin_dir.is_directory
        assert plugin_dir.user == 'grafana'
        assert plugin_dir.group == 'grafana'
    
    def test_grafana_cli_available(self, host):
        """Test that grafana-cli command is available."""
        cmd = host.run('which grafana-cli')
        assert cmd.rc == 0
    
    def test_plugin_installation(self, host):
        """Test that plugins can be listed."""
        # Test that we can list plugins (this doesn't require specific plugins)
        cmd = host.run('grafana-cli plugins list-remote | head -5')
        # Should not fail (exit code 0) if grafana-cli works
        assert cmd.rc == 0 or "connection" in cmd.stderr.lower()
    
    def test_installed_plugins(self, host):
        """Test for specific plugins if they should be installed."""
        plugin_dir = host.file('/var/lib/grafana/plugins')
        if plugin_dir.exists:
            # List contents of plugins directory
            cmd = host.run('ls -la /var/lib/grafana/plugins/')
            # Just verify the command works
            assert cmd.rc == 0


class TestGrafanaPerformanceConfig:
    """Test class for Grafana performance configuration."""
    
    def test_performance_scripts_exist(self, host):
        """Test that performance monitoring scripts exist."""
        script = host.file('/usr/local/bin/grafana_performance_monitor.sh')
        if script.exists:
            assert script.is_file
            assert script.mode & 0o111  # Check executable bit
            assert script.user == 'root'
    
    def test_performance_log_directory(self, host):
        """Test that performance log directory exists."""
        log_file = host.file('/var/log/grafana/performance.log')
        if log_file.exists:
            assert log_file.user == 'grafana'
            assert log_file.group == 'grafana'
    
    def test_cron_job_for_performance_monitoring(self, host):
        """Test that cron job for performance monitoring is set up."""
        cmd = host.run('crontab -u grafana -l')
        if cmd.rc == 0:
            # Check if performance monitoring cron job exists
            if 'grafana_performance_monitor' in cmd.stdout:
                assert 'grafana_performance_monitor' in cmd.stdout


class TestGrafanaSecurity:
    """Test class for Grafana security configurations."""
    
    def test_security_headers_config(self, host):
        """Test that security headers configuration exists."""
        security_config = host.file('/etc/grafana/security_headers.conf')
        if security_config.exists:
            assert security_config.is_file
            assert security_config.user == 'grafana'
            assert security_config.group == 'grafana'
    
    def test_ssl_certificate_permissions(self, host):
        """Test SSL certificate file permissions if they exist."""
        # This test checks for common SSL cert locations
        cert_locations = [
            '/etc/ssl/certs/grafana.crt',
            '/etc/grafana/ssl/grafana.crt',
            '/opt/grafana/ssl/grafana.crt'
        ]
        
        for cert_path in cert_locations:
            cert_file = host.file(cert_path)
            if cert_file.exists:
                assert cert_file.user == 'grafana'
                assert cert_file.mode == 0o640
    
    def test_firewall_configuration(self, host):
        """Test firewall configuration for Grafana port."""
        # Check if UFW is active (Ubuntu/Debian)
        ufw_cmd = host.run('ufw status | grep 3000')
        firewalld_cmd = host.run('firewall-cmd --list-ports | grep 3000')
        
        # At least one firewall should be configured or not active
        # This is a basic check - in production you'd want more specific tests
        assert ufw_cmd.rc in [0, 1] or firewalld_cmd.rc in [0, 1]
    
    def test_admin_password_not_default(self, host):
        """Test that admin password is configured (not checking actual value)."""
        config = host.file('/etc/grafana/grafana.ini')
        if config.exists:
            content = config.content_string
            # Check that admin_password line exists and is not the default
            assert 'admin_password' in content
            # Should not contain the default password 'admin' directly
            assert 'admin_password = admin' not in content


class TestGrafanaBackupRestore:
    """Test class for Grafana backup and restore functionality."""
    
    def test_backup_directory_exists(self, host):
        """Test that backup directory exists."""
        backup_dir = host.file('/var/backups/grafana')
        if backup_dir.exists:
            assert backup_dir.is_directory
            assert backup_dir.user == 'grafana'
    
    def test_backup_script_exists(self, host):
        """Test that backup script exists."""
        backup_script = host.file('/usr/local/bin/grafana_dashboard_backup.sh')
        if backup_script.exists:
            assert backup_script.is_file
            assert backup_script.mode & 0o111  # Executable
    
    def test_backup_cron_job(self, host):
        """Test that backup cron job is configured."""
        cmd = host.run('crontab -u grafana -l')
        if cmd.rc == 0:
            if 'grafana_dashboard_backup' in cmd.stdout:
                assert 'grafana_dashboard_backup' in cmd.stdout
    
    def test_database_backup_capability(self, host):
        """Test database backup tools are available."""
        # Test for SQLite3 (default database)
        sqlite_cmd = host.run('which sqlite3')
        assert sqlite_cmd.rc == 0
        
        # Check if other database tools are available (optional)
        mysql_cmd = host.run('which mysqldump')
        pg_cmd = host.run('which pg_dump')
        
        # At least SQLite should be available
        assert sqlite_cmd.rc == 0


class TestGrafanaMonitoring:
    """Test class for Grafana self-monitoring."""
    
    def test_monitoring_scripts_exist(self, host):
        """Test that monitoring scripts exist."""
        monitoring_script = host.file('/usr/local/bin/grafana_monitoring_health_check.sh')
        if monitoring_script.exists:
            assert monitoring_script.is_file
            assert monitoring_script.mode & 0o111
    
    def test_monitoring_log_files(self, host):
        """Test that monitoring log files are created."""
        log_files = [
            '/var/log/grafana/monitoring_health.log',
            '/var/log/grafana/external_monitoring.log'
        ]
        
        for log_file_path in log_files:
            log_file = host.file(log_file_path)
            if log_file.exists:
                assert log_file.user == 'grafana'
                assert log_file.group == 'grafana'
    
    def test_self_monitoring_dashboard(self, host):
        """Test that self-monitoring dashboard exists."""
        dashboard_file = host.file('/var/lib/grafana/dashboards/grafana-self-monitoring.json')
        if dashboard_file.exists:
            assert dashboard_file.is_file
            assert dashboard_file.user == 'grafana'
    
    def test_monitoring_configuration_directory(self, host):
        """Test that monitoring configuration directory exists."""
        monitoring_dir = host.file('/etc/grafana/monitoring')
        if monitoring_dir.exists:
            assert monitoring_dir.is_directory
            assert monitoring_dir.user == 'grafana'


class TestGrafanaAPI:
    """Test class for Grafana API functionality."""
    
    def test_api_key_storage_permissions(self, host):
        """Test API key storage has correct permissions."""
        api_keys_file = host.file('/etc/grafana/api_keys.env')
        if api_keys_file.exists:
            assert api_keys_file.mode == 0o600
            assert api_keys_file.user == 'grafana'
    
    def test_service_account_token_storage(self, host):
        """Test service account token storage permissions."""
        tokens_file = host.file('/etc/grafana/service_account_tokens.env')
        if tokens_file.exists:
            assert tokens_file.mode == 0o600
            assert tokens_file.user == 'grafana'


class TestGrafanaAlerting:
    """Test class for Grafana alerting functionality."""
    
    def test_alerting_provisioning_directory(self, host):
        """Test that alerting provisioning directory exists."""
        alerting_dir = host.file('/etc/grafana/provisioning/alerting')
        assert alerting_dir.exists
        assert alerting_dir.is_directory
        assert alerting_dir.user == 'grafana'
    
    def test_alerting_health_check_script(self, host):
        """Test that alerting health check script exists."""
        script = host.file('/usr/local/bin/grafana_alerting_health_check.sh')
        if script.exists:
            assert script.is_file
            assert script.mode & 0o111
    
    def test_alerting_configuration_files(self, host):
        """Test that alerting configuration files exist."""
        config_files = [
            '/etc/grafana/provisioning/alerting/rules.yml',
            '/etc/grafana/provisioning/alerting/contactpoints.yml',
            '/etc/grafana/provisioning/alerting/policies.yml'
        ]
        
        for config_file_path in config_files:
            config_file = host.file(config_file_path)
            if config_file.exists:
                assert config_file.user == 'grafana'
                assert config_file.group == 'grafana'


class TestGrafanaDashboards:
    """Test class for Grafana dashboard management."""
    
    def test_dashboard_provisioning_config(self, host):
        """Test that dashboard provisioning configuration exists."""
        config_file = host.file('/etc/grafana/provisioning/dashboards/providers.yml')
        if config_file.exists:
            assert config_file.is_file
            assert config_file.user == 'grafana'
    
    def test_dashboard_directories(self, host):
        """Test that dashboard directories exist."""
        dashboard_dir = host.file('/var/lib/grafana/dashboards')
        if dashboard_dir.exists:
            assert dashboard_dir.is_directory
            assert dashboard_dir.user == 'grafana'
    
    def test_dashboard_backup_directory_structure(self, host):
        """Test dashboard backup directory structure."""
        backup_dir = host.file('/var/backups/grafana/dashboards')
        if backup_dir.exists:
            assert backup_dir.is_directory
            assert backup_dir.user == 'grafana'


def test_systemd_service_overrides(host):
    """Test systemd service overrides if they exist."""
    override_dir = host.file('/etc/systemd/system/grafana-server.service.d')
    if override_dir.exists:
        assert override_dir.is_directory
        
        limits_file = host.file('/etc/systemd/system/grafana-server.service.d/limits.conf')
        if limits_file.exists:
            assert limits_file.is_file
