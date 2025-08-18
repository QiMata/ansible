import os
import pytest
import requests
import testinfra.utils.ansible_runner
import time

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_minio_binary(host):
    f = host.file('/usr/local/bin/minio')
    assert f.exists
    assert f.mode & 0o111

def test_minio_user(host):
    u = host.user('minio')
    assert u.exists

def test_directories(host):
    for path in ['/opt/minio', '/opt/minio/data', '/opt/minio/certs']:
        d = host.file(path)
        assert d.is_directory
        assert d.user == 'minio'

def test_env_file(host):
    env = host.file('/etc/default/minio')
    assert env.exists
    content = env.content_string
    assert 'MINIO_ROOT_USER' in content
    assert 'MINIO_ROOT_PASSWORD' in content
    assert 'MINIO_VOLUMES' in content

def test_service_running(host):
    svc = host.service('minio')
    assert svc.is_enabled
    assert svc.is_running
    assert host.socket('tcp://0.0.0.0:9000').is_listening
    assert host.socket('tcp://0.0.0.0:9001').is_listening

def test_minio_health_endpoint(host):
    """Test that MinIO health endpoint is responding."""
    time.sleep(15)  # Give MinIO time to fully start
    
    try:
        response = requests.get("http://localhost:9000/minio/health/live", timeout=30)
        assert response.status_code == 200
    except requests.ConnectionError:
        pytest.fail("Could not connect to MinIO health endpoint")

def test_mc_client_installed_when_needed(host):
    """Test that MinIO client is installed when user management is enabled."""
    variables = host.ansible.get_variables()
    user_mgmt_enabled = (
        variables.get('minio_create_users', []) or
        variables.get('minio_create_buckets', []) or
        variables.get('minio_bucket_policies', [])
    )
    
    if user_mgmt_enabled:
        mc_binary = host.file("/usr/local/bin/mc")
        assert mc_binary.exists
        assert mc_binary.is_file
        assert mc_binary.mode & 0o111

def test_monitoring_scripts(host):
    """Test that monitoring scripts are created."""
    script = host.file("/opt/minio/disk_usage_monitor.sh")
    assert script.exists
    assert script.is_file
    assert script.user == "minio"
    assert script.mode & 0o111

def test_log_directories(host):
    """Test that log directories are created."""
    log_dir = host.file("/opt/minio/logs")
    assert log_dir.exists
    assert log_dir.is_directory
    assert log_dir.user == "minio"
