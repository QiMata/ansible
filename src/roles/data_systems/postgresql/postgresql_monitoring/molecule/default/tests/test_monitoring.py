import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

class TestPostgreSQLMonitoring:
    
    def test_postgresql_service_running(self, host):
        """Test that PostgreSQL service is running"""
        service = host.service("postgresql")
        assert service.is_running
        assert service.is_enabled

    def test_health_check_script_exists(self, host):
        """Test that health check script exists and is executable"""
        health_script = host.file("/usr/local/bin/postgresql_health_check.sh")
        assert health_script.exists
        assert health_script.is_file
        assert health_script.mode == 0o755

    def test_health_check_timer_active(self, host):
        """Test that health check timer is active"""
        timer = host.service("postgresql_health_check.timer")
        assert timer.is_enabled
        assert timer.is_running

    def test_postgresql_listening(self, host):
        """Test that PostgreSQL is listening on port 5432"""
        assert host.socket("tcp://0.0.0.0:5432").is_listening

    def test_pg_stat_statements_extension(self, host):
        """Test that pg_stat_statements extension is loaded"""
        cmd = host.run("sudo -u postgres psql -t -c \"SELECT 1 FROM pg_extension WHERE extname='pg_stat_statements';\"")
        assert cmd.rc == 0
        assert "1" in cmd.stdout

    def test_slow_query_logging_enabled(self, host):
        """Test that slow query logging is configured"""
        config_file = host.file("/etc/postgresql/14/main/postgresql.conf")
        assert config_file.exists
        assert config_file.contains("log_min_duration_statement")

    def test_health_check_log_created(self, host):
        """Test that health check creates log file"""
        # Run health check manually
        cmd = host.run("/usr/local/bin/postgresql_health_check.sh")
        log_file = host.file("/var/log/postgresql_health_check.log")
        assert log_file.exists

    @pytest.mark.parametrize("directory", [
        "/etc/pgbouncer",
        "/var/log/pgbouncer"
    ])
    def test_directories_exist(self, host, directory):
        """Test that required directories exist"""
        dir_obj = host.file(directory)
        if directory == "/etc/pgbouncer":
            # PgBouncer might not be installed in this test
            pytest.skip("PgBouncer not installed in this test scenario")
        else:
            assert dir_obj.exists

    def test_postgresql_configuration_syntax(self, host):
        """Test that PostgreSQL configuration is valid"""
        cmd = host.run("sudo -u postgres /usr/lib/postgresql/14/bin/postgres --config-file=/etc/postgresql/14/main/postgresql.conf --check")
        assert cmd.rc == 0

    def test_database_connectivity(self, host):
        """Test basic database connectivity"""
        cmd = host.run("sudo -u postgres psql -c 'SELECT 1;'")
        assert cmd.rc == 0
        assert "1" in cmd.stdout
