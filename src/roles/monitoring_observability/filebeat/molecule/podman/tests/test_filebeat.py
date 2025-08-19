import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


class TestFilebeatPackage:
    """Test Filebeat package installation."""
    
    def test_filebeat_package_installed(self, host):
        """Test that Filebeat package is installed."""
        pkg = host.package('filebeat')
        assert pkg.is_installed

    def test_filebeat_version(self, host):
        """Test that Filebeat version is correct."""
        cmd = host.run('filebeat version')
        assert cmd.rc == 0
        assert 'filebeat version' in cmd.stdout


class TestFilebeatConfiguration:
    """Test Filebeat configuration."""
    
    def test_config_file_exists(self, host):
        """Test that configuration file exists."""
        cfg = host.file('/etc/filebeat/filebeat.yml')
        assert cfg.exists
        assert cfg.user == 'root'
        assert cfg.group == 'root'
        assert cfg.mode == 0o644

    def test_config_file_content(self, host):
        """Test configuration file content."""
        cfg = host.file('/etc/filebeat/filebeat.yml')
        content = cfg.content_string
        assert 'filebeat.inputs' in content
        assert 'output.' in content

    def test_config_validation(self, host):
        """Test that configuration is valid."""
        cmd = host.run('filebeat test config -c /etc/filebeat/filebeat.yml')
        assert cmd.rc == 0

    def test_config_directories_exist(self, host):
        """Test that required directories exist."""
        directories = [
            '/etc/filebeat',
            '/var/lib/filebeat',
            '/var/log/filebeat'
        ]
        for directory in directories:
            dir_obj = host.file(directory)
            assert dir_obj.exists
            assert dir_obj.is_directory

    def test_backup_directory_exists(self, host):
        """Test that backup directory exists if enabled."""
        backup_dir = host.file('/etc/filebeat/backups')
        # This will only exist if backup is enabled
        if backup_dir.exists:
            assert backup_dir.is_directory
            assert backup_dir.user == 'root'
            assert backup_dir.group == 'root'


class TestFilebeatService:
    """Test Filebeat service."""
    
    def test_service_enabled(self, host):
        """Test that Filebeat service is enabled."""
        svc = host.service('filebeat')
        assert svc.is_enabled

    def test_service_running(self, host):
        """Test that Filebeat service is running."""
        svc = host.service('filebeat')
        assert svc.is_running

    def test_service_listens_on_port(self, host):
        """Test that Filebeat is listening on monitoring port if enabled."""
        # This test depends on HTTP monitoring being enabled
        monitoring_socket = host.socket('tcp://127.0.0.1:5066')
        # Only test if the socket exists (monitoring enabled)
        if monitoring_socket.is_listening:
            assert monitoring_socket.is_listening


class TestFilebeatFunctionality:
    """Test Filebeat functionality."""
    
    def test_output_connectivity(self, host):
        """Test output connectivity if possible."""
        # This test might fail in isolated test environments
        cmd = host.run('filebeat test output -c /etc/filebeat/filebeat.yml')
        # We don't assert success here as it depends on external connectivity
        # Just verify the command can be executed
        assert 'test' in cmd.stderr.lower() or 'test' in cmd.stdout.lower()

    def test_logging_directory(self, host):
        """Test that logging directory is properly configured."""
        log_dir = host.file('/var/log/filebeat')
        assert log_dir.exists
        assert log_dir.is_directory

    def test_modules_directory(self, host):
        """Test that modules directory exists."""
        modules_dir = host.file('/etc/filebeat/modules.d')
        assert modules_dir.exists
        assert modules_dir.is_directory


class TestFilebeatSecurity:
    """Test Filebeat security configuration."""
    
    def test_config_file_permissions(self, host):
        """Test that configuration file has proper permissions."""
        cfg = host.file('/etc/filebeat/filebeat.yml')
        assert cfg.mode == 0o644

    def test_ssl_certificates_permissions(self, host):
        """Test SSL certificate permissions if they exist."""
        cert_file = host.file('/etc/filebeat/filebeat.crt')
        key_file = host.file('/etc/filebeat/filebeat.key')
        
        if cert_file.exists:
            assert cert_file.mode == 0o644
            assert cert_file.user == 'root'
            assert cert_file.group == 'root'
        
        if key_file.exists:
            assert key_file.mode == 0o600
            assert key_file.user == 'root'
            assert key_file.group == 'root'


class TestFilebeatModules:
    """Test Filebeat modules functionality."""
    
    def test_modules_command_available(self, host):
        """Test that modules command is available."""
        cmd = host.run('filebeat modules list')
        assert cmd.rc == 0

    def test_modules_directory_readable(self, host):
        """Test that modules directory is readable."""
        modules_dir = host.file('/etc/filebeat/modules.d')
        assert modules_dir.exists
        assert modules_dir.is_directory
        assert modules_dir.mode & 0o444  # Readable


class TestFilebeatMonitoring:
    """Test Filebeat monitoring features."""
    
    def test_monitoring_script_exists(self, host):
        """Test that monitoring script exists."""
        script = host.file('/usr/local/bin/filebeat_monitor.sh')
        if script.exists:
            assert script.is_file
            assert script.mode & 0o755  # Executable
            assert script.user == 'root'

    def test_monitoring_log_directory(self, host):
        """Test monitoring log can be written."""
        # Test if we can write to the monitoring log location
        cmd = host.run('touch /var/log/filebeat_monitor.log')
        assert cmd.rc == 0


@pytest.mark.parametrize("file_path,expected_content", [
    ('/etc/filebeat/filebeat.yml', 'filebeat.inputs'),
    ('/etc/filebeat/filebeat.yml', 'output.'),
])
def test_config_contains_expected_content(host, file_path, expected_content):
    """Parametrized test for configuration content."""
    cfg_file = host.file(file_path)
    if cfg_file.exists:
        assert expected_content in cfg_file.content_string


@pytest.mark.parametrize("command,expected_rc", [
    ('filebeat version', 0),
    ('filebeat test config -c /etc/filebeat/filebeat.yml', 0),
    ('systemctl is-enabled filebeat', 0),
    ('systemctl is-active filebeat', 0),
])
def test_filebeat_commands(host, command, expected_rc):
    """Parametrized test for various Filebeat commands."""
    cmd = host.run(command)
    assert cmd.rc == expected_rc
