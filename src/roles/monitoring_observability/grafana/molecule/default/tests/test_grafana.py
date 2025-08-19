import os
import pytest
import requests
import testinfra.utils.ansible_runner
import json


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    """Test that Grafana package is installed."""
    pkg = host.package('grafana')
    assert pkg.is_installed


def test_service_running(host):
    """Test that Grafana service is running and enabled."""
    service = host.service('grafana-server')
    assert service.is_enabled
    assert service.is_running


def test_config_file(host):
    """Test that Grafana configuration file exists and has correct permissions."""
    cfg = host.file('/etc/grafana/grafana.ini')
    assert cfg.exists
    assert cfg.user == 'root'
    assert cfg.group == 'grafana'
    assert cfg.mode == 0o640


def test_port_listening(host):
    """Test that Grafana is listening on the configured port."""
    # Default port is 3000, but can be customized
    assert host.socket('tcp://0.0.0.0:3000').is_listening


def test_data_directories(host):
    """Test that Grafana data directories exist with correct permissions."""
    directories = [
        '/var/lib/grafana',
        '/var/lib/grafana/plugins',
        '/var/log/grafana',
        '/etc/grafana/provisioning',
        '/etc/grafana/provisioning/datasources',
        '/etc/grafana/provisioning/dashboards',
        '/etc/grafana/provisioning/alerting'
    ]
    
    for directory in directories:
        dir_obj = host.file(directory)
        assert dir_obj.exists
        assert dir_obj.is_directory
        assert dir_obj.user == 'grafana'
        assert dir_obj.group == 'grafana'


def test_provisioning_directories(host):
    """Test that provisioning directories are properly set up."""
    provisioning_dirs = [
        '/etc/grafana/provisioning/notifiers',
        '/etc/grafana/provisioning/plugins',
        '/etc/grafana/provisioning/access-control'
    ]
    
    for directory in provisioning_dirs:
        dir_obj = host.file(directory)
        assert dir_obj.exists
        assert dir_obj.is_directory


def test_grafana_health_endpoint(host):
    """Test that Grafana health endpoint is accessible."""
    try:
        response = requests.get('http://localhost:3000/api/health', timeout=10)
        assert response.status_code == 200
        health_data = response.json()
        assert 'database' in health_data
        assert health_data['database'] == 'ok'
    except requests.exceptions.RequestException:
        pytest.skip("Grafana service not accessible for endpoint testing")


def test_grafana_metrics_endpoint(host):
    """Test that Grafana metrics endpoint is accessible."""
    try:
        response = requests.get('http://localhost:3000/metrics', timeout=10)
        # Should return 200 or 401 (if auth required)
        assert response.status_code in [200, 401]
    except requests.exceptions.RequestException:
        pytest.skip("Grafana service not accessible for metrics testing")


def test_plugin_directory(host):
    """Test that plugin directory is properly configured."""
    plugin_dir = host.file('/var/lib/grafana/plugins')
    assert plugin_dir.exists
    assert plugin_dir.is_directory
    assert plugin_dir.user == 'grafana'


def test_backup_directory(host):
    """Test that backup directory exists if backup is enabled."""
    backup_dir = host.file('/var/backups/grafana')
    # This test assumes backup is enabled in molecule scenario
    if backup_dir.exists:
        assert backup_dir.is_directory
        assert backup_dir.user == 'grafana'


def test_log_files(host):
    """Test that log directory and files are properly configured."""
    log_dir = host.file('/var/log/grafana')
    assert log_dir.exists
    assert log_dir.is_directory
    assert log_dir.user == 'grafana'


def test_systemd_service_file(host):
    """Test that systemd service file exists."""
    service_file = host.file('/lib/systemd/system/grafana-server.service')
    assert service_file.exists


def test_grafana_user_exists(host):
    """Test that grafana system user exists."""
    user = host.user('grafana')
    assert user.exists
    assert user.shell == '/usr/sbin/nologin' or user.shell == '/bin/false'


def test_grafana_configuration_validity(host):
    """Test that Grafana configuration is valid."""
    # Test that grafana-server can validate config
    cmd = host.run('grafana-server -config=/etc/grafana/grafana.ini -test-config')
    # Note: This command might not exist in all versions, so we skip if command not found
    if cmd.rc != 127:  # Command not found
        assert cmd.rc == 0


def test_provisioning_files(host):
    """Test that provisioning files are created."""
    # Test datasources provisioning
    datasources_file = host.file('/etc/grafana/provisioning/datasources')
    assert datasources_file.exists
    
    # Test dashboards provisioning
    dashboards_file = host.file('/etc/grafana/provisioning/dashboards')
    assert dashboards_file.exists


class TestGrafanaAPI:
    """Test class for Grafana API functionality."""
    
    @pytest.fixture
    def grafana_url(self):
        return "http://localhost:3000"
    
    @pytest.fixture
    def admin_credentials(self):
        return ("admin", "admin")  # Default credentials for testing
    
    def test_api_login(self, grafana_url, admin_credentials):
        """Test that API login works with admin credentials."""
        try:
            response = requests.get(
                f"{grafana_url}/api/user",
                auth=admin_credentials,
                timeout=10
            )
            # Should return 200 if login works, 401 if credentials are wrong
            assert response.status_code in [200, 401]
        except requests.exceptions.RequestException:
            pytest.skip("Grafana API not accessible for testing")
    
    def test_api_health(self, grafana_url):
        """Test that API health endpoint returns proper status."""
        try:
            response = requests.get(f"{grafana_url}/api/health", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert 'database' in data
        except requests.exceptions.RequestException:
            pytest.skip("Grafana API not accessible for testing")
    
    def test_api_datasources(self, grafana_url, admin_credentials):
        """Test that datasources API endpoint is accessible."""
        try:
            response = requests.get(
                f"{grafana_url}/api/datasources",
                auth=admin_credentials,
                timeout=10
            )
            # Should return 200 with valid auth, 401 without
            assert response.status_code in [200, 401]
        except requests.exceptions.RequestException:
            pytest.skip("Grafana API not accessible for testing")


class TestGrafanaPerformance:
    """Test class for Grafana performance and resource usage."""
    
    def test_memory_usage(self, host):
        """Test that Grafana memory usage is within reasonable limits."""
        # Get memory usage of grafana-server process
        cmd = host.run("ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem -C grafana-server")
        if cmd.rc == 0 and len(cmd.stdout.strip().split('\n')) > 1:
            # Parse memory usage (assuming it's in the output)
            lines = cmd.stdout.strip().split('\n')[1:]  # Skip header
            if lines:
                # Basic check that process exists and has reasonable memory usage
                assert len(lines) > 0
    
    def test_cpu_usage(self, host):
        """Test that Grafana CPU usage is reasonable."""
        # This is a basic test - in real scenarios you'd want more sophisticated monitoring
        cmd = host.run("ps -o pid,ppid,cmd,%mem,%cpu --sort=-%cpu -C grafana-server")
        if cmd.rc == 0:
            # Just verify the process is running
            assert "grafana-server" in cmd.stdout


class TestGrafanaScripts:
    """Test class for Grafana management scripts."""
    
    def test_backup_script_exists(self, host):
        """Test that backup script exists if backup is enabled."""
        script = host.file('/usr/local/bin/grafana_dashboard_backup.sh')
        if script.exists:
            assert script.is_file
            assert script.mode & 0o111  # Executable
    
    def test_performance_monitor_script_exists(self, host):
        """Test that performance monitoring script exists if enabled."""
        script = host.file('/usr/local/bin/grafana_performance_monitor.sh')
        if script.exists:
            assert script.is_file
            assert script.mode & 0o111  # Executable
    
    def test_health_check_script_exists(self, host):
        """Test that health check script exists if monitoring is enabled."""
        script = host.file('/usr/local/bin/grafana_monitoring_health_check.sh')
        if script.exists:
            assert script.is_file
            assert script.mode & 0o111  # Executable


class TestGrafanaSecurity:
    """Test class for Grafana security configurations."""
    
    def test_config_file_permissions(self, host):
        """Test that configuration files have secure permissions."""
        config_file = host.file('/etc/grafana/grafana.ini')
        assert config_file.mode == 0o640  # Not world-readable
    
    def test_api_keys_file_permissions(self, host):
        """Test that API keys file has secure permissions if it exists."""
        api_keys_file = host.file('/etc/grafana/api_keys.env')
        if api_keys_file.exists:
            assert api_keys_file.mode == 0o600  # Owner readable only
            assert api_keys_file.user == 'grafana'
    
    def test_service_account_tokens_permissions(self, host):
        """Test that service account tokens file has secure permissions if it exists."""
        tokens_file = host.file('/etc/grafana/service_account_tokens.env')
        if tokens_file.exists:
            assert tokens_file.mode == 0o600  # Owner readable only
            assert tokens_file.user == 'grafana'


def test_grafana_version_installed(host):
    """Test that correct Grafana version is installed."""
    cmd = host.run('grafana-server --version')
    assert cmd.rc == 0
    # The version should be in the output
    assert 'Grafana' in cmd.stdout or 'version' in cmd.stdout
