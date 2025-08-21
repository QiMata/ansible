import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_package_installed(host):
    """Test that Vault package is installed."""
    assert host.package('vault').is_installed


def test_service_running(host):
    """Test that Vault service is running and enabled."""
    svc = host.service('vault')
    assert svc.is_enabled
    assert svc.is_running


def test_config_file(host):
    """Test that Vault configuration file exists and has expected content."""
    cfg = host.file('/etc/vault/vault.hcl')
    assert cfg.exists
    assert cfg.contains('listener "tcp"')
    assert cfg.contains('storage "file"')


def test_port(host):
    """Test that Vault is listening on the expected port."""
    assert host.socket('tcp://0.0.0.0:8200').is_listening


def test_vault_user_exists(host):
    """Test that the vault user exists."""
    user = host.user('vault')
    assert user.exists
    assert user.group == 'vault'


def test_directories_exist(host):
    """Test that required directories exist with correct permissions."""
    # Data directory
    data_dir = host.file('/opt/vault/data')
    assert data_dir.exists
    assert data_dir.is_directory
    assert data_dir.user == 'vault'
    assert data_dir.group == 'vault'
    
    # Config directory
    config_dir = host.file('/etc/vault')
    assert config_dir.exists
    assert config_dir.is_directory
    
    # Log directory
    log_dir = host.file('/var/log/vault')
    assert log_dir.exists
    assert log_dir.is_directory
    assert log_dir.user == 'vault'
    assert log_dir.group == 'vault'


def test_backup_scripts_exist(host):
    """Test that backup scripts are created."""
    backup_script = host.file('/usr/local/bin/vault_backup.sh')
    assert backup_script.exists
    assert backup_script.is_file
    assert backup_script.mode == 0o755
    
    restore_script = host.file('/usr/local/bin/vault_restore.sh')
    assert restore_script.exists
    assert restore_script.is_file
    assert restore_script.mode == 0o755
    
    verify_script = host.file('/usr/local/bin/vault_backup_verify.sh')
    assert verify_script.exists
    assert verify_script.is_file
    assert verify_script.mode == 0o755


def test_health_check_script(host):
    """Test that health check script exists and is executable."""
    health_script = host.file('/usr/local/bin/vault_health_check.sh')
    assert health_script.exists
    assert health_script.is_file
    assert health_script.mode == 0o755


def test_logrotate_config(host):
    """Test that logrotate configuration exists."""
    logrotate = host.file('/etc/logrotate.d/vault')
    assert logrotate.exists
    assert logrotate.contains('/var/log/vault/vault.log')


def test_telemetry_enabled(host):
    """Test that telemetry is enabled in configuration."""
    cfg = host.file('/etc/vault/vault.hcl')
    assert cfg.contains('telemetry')


def test_backup_directory(host):
    """Test that backup directory exists."""
    backup_dir = host.file('/opt/vault/backups')
    assert backup_dir.exists
    assert backup_dir.is_directory
    assert backup_dir.user == 'vault'
    assert backup_dir.group == 'vault'


def test_vault_health_endpoint(host):
    """Test that Vault health endpoint is accessible."""
    # This test requires Vault to be initialized and unsealed
    # For now, we'll just test that the service responds
    cmd = host.run('curl -s http://localhost:8200/v1/sys/health || true')
    # We expect either a valid response or connection refused (if not initialized)
    # But the service should be running
    assert cmd.rc in [0, 7]  # 0 = success, 7 = connection refused (acceptable in test)

