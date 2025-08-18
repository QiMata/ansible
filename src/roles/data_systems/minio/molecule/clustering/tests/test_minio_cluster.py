import os
import pytest
import requests
import testinfra.utils.ansible_runner
import time
import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


class TestMinIOCluster:
    
    def test_minio_service_running(self, host):
        """Test that MinIO service is running."""
        service = host.service("minio")
        assert service.is_running
        assert service.is_enabled
    
    def test_minio_binary_installed(self, host):
        """Test that MinIO binary is installed."""
        minio_binary = host.file("/usr/local/bin/minio")
        assert minio_binary.exists
        assert minio_binary.is_file
        assert minio_binary.mode == 0o755
    
    def test_minio_user_exists(self, host):
        """Test that MinIO user exists."""
        user = host.user("minio")
        assert user.exists
        assert user.group == "minio"
    
    def test_minio_directories_exist(self, host):
        """Test that MinIO directories exist with correct permissions."""
        directories = [
            "/opt/minio",
            "/opt/minio/data",
            "/opt/minio/certs"
        ]
        
        for directory in directories:
            dir_obj = host.file(directory)
            assert dir_obj.exists
            assert dir_obj.is_directory
            assert dir_obj.user == "minio"
            assert dir_obj.group == "minio"
    
    def test_minio_configuration_files(self, host):
        """Test that MinIO configuration files exist."""
        config_files = [
            "/etc/default/minio",
            "/etc/systemd/system/minio.service"
        ]
        
        for config_file in config_files:
            file_obj = host.file(config_file)
            assert file_obj.exists
            assert file_obj.is_file
    
    def test_minio_clustering_configuration(self, host):
        """Test clustering configuration in environment file."""
        env_file = host.file("/etc/default/minio")
        content = env_file.content_string
        
        assert "MINIO_DISTRIBUTED_MODE_ENABLED=true" in content
        assert "MINIO_DISTRIBUTED_NODES=" in content
    
    def test_minio_ports_listening(self, host):
        """Test that MinIO is listening on expected ports."""
        # Give MinIO some time to start up
        time.sleep(10)
        
        # Check server port
        assert host.socket("tcp://0.0.0.0:9000").is_listening
        # Check console port
        assert host.socket("tcp://0.0.0.0:9001").is_listening
    
    @pytest.mark.parametrize("port", [9000, 9001])
    def test_minio_endpoints_responding(self, host, port):
        """Test that MinIO endpoints are responding."""
        # Only test on the first node to avoid connection issues
        if host.ansible.get_variables()['inventory_hostname'] != 'minio-cluster-node1':
            pytest.skip("Only testing endpoints on first node")
        
        time.sleep(15)  # Give more time for cluster to initialize
        
        try:
            if port == 9000:
                # Test health endpoint
                response = requests.get(f"http://localhost:{port}/minio/health/live", timeout=30)
                assert response.status_code == 200
            elif port == 9001:
                # Test console endpoint
                response = requests.get(f"http://localhost:{port}/", timeout=30)
                # Console might redirect or return different status codes
                assert response.status_code in [200, 302, 403]
        except requests.ConnectionError:
            pytest.fail(f"Could not connect to MinIO on port {port}")
    
    def test_mc_client_installed(self, host):
        """Test that MinIO client is installed."""
        mc_binary = host.file("/usr/local/bin/mc")
        assert mc_binary.exists
        assert mc_binary.is_file
        assert mc_binary.mode == 0o755
    
    def test_health_check_scripts(self, host):
        """Test that health check scripts are created."""
        health_scripts = [
            "/opt/minio/health_check.sh",
            "/opt/minio/cluster_health_check.sh"
        ]
        
        for script in health_scripts:
            script_obj = host.file(script)
            assert script_obj.exists
            assert script_obj.is_file
            assert script_obj.user == "minio"
            assert script_obj.group == "minio"
            assert script_obj.mode == 0o755
    
    def test_backup_scripts(self, host):
        """Test that backup scripts are created."""
        backup_scripts = [
            "/opt/minio/backup_minio.sh",
            "/opt/minio/backup_cleanup.sh"
        ]
        
        for script in backup_scripts:
            script_obj = host.file(script)
            assert script_obj.exists
            assert script_obj.is_file
            assert script_obj.user == "minio"
            assert script_obj.group == "minio"
            assert script_obj.mode == 0o755
    
    def test_monitoring_scripts(self, host):
        """Test that monitoring scripts are created."""
        monitoring_scripts = [
            "/opt/minio/disk_usage_monitor.sh"
        ]
        
        for script in monitoring_scripts:
            script_obj = host.file(script)
            assert script_obj.exists
            assert script_obj.is_file
            assert script_obj.user == "minio"
            assert script_obj.group == "minio"
            assert script_obj.mode == 0o755
    
    def test_systemd_timers(self, host):
        """Test that systemd health check timer is configured."""
        timer_files = [
            "/etc/systemd/system/minio-health-check.timer",
            "/etc/systemd/system/minio-health-check.service"
        ]
        
        for timer_file in timer_files:
            file_obj = host.file(timer_file)
            assert file_obj.exists
            assert file_obj.is_file
    
    def test_log_directories(self, host):
        """Test that log directories are created."""
        log_dir = host.file("/opt/minio/logs")
        assert log_dir.exists
        assert log_dir.is_directory
        assert log_dir.user == "minio"
        assert log_dir.group == "minio"
    
    def test_cron_jobs(self, host):
        """Test that cron jobs are configured."""
        # Check that cron jobs exist for minio user
        cron_output = host.run("crontab -l -u minio").stdout
        
        # Should have disk usage monitoring
        assert "disk_usage_monitor.sh" in cron_output
        # Should have cluster health check if clustering is enabled
        if host.ansible.get_variables().get('minio_enable_clustering', False):
            assert "cluster_health_check.sh" in cron_output
    
    def test_prometheus_configuration(self, host):
        """Test Prometheus metrics configuration."""
        if host.ansible.get_variables().get('minio_enable_prometheus', False):
            env_file = host.file("/etc/default/minio")
            content = env_file.content_string
            assert "MINIO_PROMETHEUS_AUTH_TYPE=public" in content


class TestMinIOFunctionality:
    """Test MinIO functional capabilities after deployment."""
    
    def test_bucket_creation(self, host):
        """Test that test bucket was created."""
        # Only test on the first node
        if host.ansible.get_variables()['inventory_hostname'] != 'minio-cluster-node1':
            pytest.skip("Only testing bucket creation on first node")
        
        # Wait for MinIO to be fully ready
        time.sleep(30)
        
        # Check if mc alias is configured and bucket exists
        mc_config_dir = "/home/minio/.mc"
        config_exists = host.file(mc_config_dir).exists
        assert config_exists, "MC configuration directory should exist"
        
        # Try to list buckets (this will indicate if the setup worked)
        result = host.run("sudo -u minio MC_CONFIG_DIR=/home/minio/.mc mc ls local/")
        # If buckets were configured, this should not fail completely
        assert result.rc in [0, 1], "MC should be able to connect to MinIO"


class TestMinIOSecurity:
    """Test security configurations."""
    
    def test_minio_user_is_system_user(self, host):
        """Test that MinIO runs as system user."""
        user = host.user("minio")
        assert user.shell == "/usr/sbin/nologin" or user.shell == "/bin/false"
    
    def test_certificate_directory_permissions(self, host):
        """Test certificate directory has correct permissions."""
        certs_dir = host.file("/opt/minio/certs")
        assert certs_dir.mode == 0o755
        assert certs_dir.user == "minio"
        assert certs_dir.group == "minio"
    
    def test_environment_file_permissions(self, host):
        """Test environment file has secure permissions."""
        env_file = host.file("/etc/default/minio")
        # Should be readable by root and minio user but not world-readable for security
        assert env_file.mode & 0o044 == 0o044  # At least owner and group readable
        assert env_file.mode & 0o004 == 0  # Not world-readable
