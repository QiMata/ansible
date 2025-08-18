"""
Enhanced Neo4j Role Tests
Tests for all new functionality including clustering, plugins, security, etc.
"""

import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


class TestNeo4jBasicInstallation:
    """Test basic Neo4j installation and service"""

    def test_neo4j_package_installed(self, host):
        """Test that Neo4j package is installed"""
        neo4j_package = host.package('neo4j')
        assert neo4j_package.is_installed

    def test_neo4j_service_running(self, host):
        """Test that Neo4j service is running"""
        neo4j_service = host.service('neo4j')
        assert neo4j_service.is_running
        assert neo4j_service.is_enabled

    def test_neo4j_ports_listening(self, host):
        """Test that Neo4j is listening on expected ports"""
        # Bolt port
        assert host.socket('tcp://0.0.0.0:7687').is_listening
        # HTTP port (if enabled)
        if host.ansible.get_variables().get('neo4j_http_enabled', False):
            assert host.socket('tcp://0.0.0.0:7474').is_listening
        # HTTPS port
        if host.ansible.get_variables().get('neo4j_https_enabled', True):
            assert host.socket('tcp://0.0.0.0:7473').is_listening


class TestNeo4jConfiguration:
    """Test Neo4j configuration files and settings"""

    def test_neo4j_config_file_exists(self, host):
        """Test that Neo4j configuration file exists"""
        config_file = host.file('/etc/neo4j/neo4j.conf')
        assert config_file.exists
        assert config_file.user == 'root'
        assert config_file.group == 'neo4j'

    def test_neo4j_directories_exist(self, host):
        """Test that Neo4j directories exist with correct permissions"""
        directories = [
            '/var/lib/neo4j',
            '/var/log/neo4j',
            '/var/lib/neo4j/plugins',
            '/var/lib/neo4j/import'
        ]
        for directory in directories:
            dir_obj = host.file(directory)
            assert dir_obj.exists
            assert dir_obj.is_directory
            assert dir_obj.user == 'neo4j'
            assert dir_obj.group == 'neo4j'


class TestNeo4jPlugins:
    """Test Neo4j plugin installation and configuration"""

    def test_plugins_directory_exists(self, host):
        """Test that plugins directory exists"""
        plugins_dir = host.file('/var/lib/neo4j/plugins')
        assert plugins_dir.exists
        assert plugins_dir.is_directory
        assert plugins_dir.user == 'neo4j'

    def test_apoc_plugin_installed(self, host):
        """Test that APOC plugin is installed when enabled"""
        plugins = host.ansible.get_variables().get('neo4j_plugins', [])
        apoc_enabled = any(
            plugin.get('name') == 'apoc' and plugin.get('enabled', True)
            for plugin in plugins
        )
        
        if apoc_enabled:
            # Check for APOC jar file
            apoc_files = host.check_output(
                'find /var/lib/neo4j/plugins -name "*apoc*.jar"'
            )
            assert apoc_files.strip() != ""


class TestNeo4jSecurity:
    """Test Neo4j security features"""

    def test_tls_directories_exist(self, host):
        """Test that TLS directories exist when TLS is enabled"""
        tls_enabled = (
            host.ansible.get_variables().get('neo4j_tls_client_enable', False) or
            host.ansible.get_variables().get('neo4j_tls_cluster_enable', False)
        )
        
        if tls_enabled:
            tls_dirs = [
                '/etc/neo4j/certificates/bolt',
                '/etc/neo4j/certificates/cluster'
            ]
            for tls_dir in tls_dirs:
                dir_obj = host.file(tls_dir)
                assert dir_obj.exists
                assert dir_obj.is_directory
                assert dir_obj.user == 'root'
                assert dir_obj.group == 'neo4j'

    def test_audit_logging_configured(self, host):
        """Test audit logging configuration when enabled"""
        audit_enabled = host.ansible.get_variables().get('neo4j_audit_enabled', False)
        
        if audit_enabled:
            audit_dir = host.file('/var/log/neo4j/security')
            assert audit_dir.exists
            assert audit_dir.is_directory
            assert audit_dir.user == 'neo4j'


class TestNeo4jBackup:
    """Test Neo4j backup functionality"""

    def test_backup_directory_exists(self, host):
        """Test that backup directory exists when backup is enabled"""
        backup_enabled = host.ansible.get_variables().get('neo4j_backup_enabled', False)
        
        if backup_enabled:
            backup_dir = host.file('/var/backups/neo4j')
            assert backup_dir.exists
            assert backup_dir.is_directory

    def test_backup_scripts_exist(self, host):
        """Test that backup scripts exist when backup is enabled"""
        backup_enabled = host.ansible.get_variables().get('neo4j_backup_enabled', False)
        individual_backup = host.ansible.get_variables().get('neo4j_database_backup_individual', False)
        
        if backup_enabled and individual_backup:
            backup_script = host.file('/usr/local/bin/neo4j-database-backup.sh')
            assert backup_script.exists
            assert backup_script.is_file
            assert backup_script.mode == 0o755


class TestNeo4jClustering:
    """Test Neo4j clustering functionality"""

    @pytest.mark.skipif("'neo4j_core' not in group_names")
    def test_cluster_configuration(self, host):
        """Test cluster configuration for core members"""
        cluster_enabled = host.ansible.get_variables().get('neo4j_cluster_enabled', False)
        
        if cluster_enabled:
            config_file = host.file('/etc/neo4j/neo4j.conf')
            content = config_file.content_string
            
            # Check for cluster-specific configuration
            assert 'dbms.cluster.discovery.type=' in content
            assert 'dbms.mode=CORE' in content or 'dbms.mode=READ_REPLICA' in content


class TestNeo4jMonitoring:
    """Test Neo4j monitoring and health checks"""

    def test_health_check_scripts_exist(self, host):
        """Test that health check scripts exist"""
        health_script = host.file('/usr/local/bin/neo4j-health-check.sh')
        assert health_script.exists
        assert health_script.is_file
        assert health_script.mode == 0o755

    def test_jmx_configuration(self, host):
        """Test JMX configuration when enabled"""
        jmx_enabled = host.ansible.get_variables().get('neo4j_jmx_enabled', False)
        
        if jmx_enabled:
            jmx_port = host.ansible.get_variables().get('neo4j_jmx_port', 3637)
            # Note: JMX port might not be listening in test environment
            # Just check configuration exists
            config_file = host.file('/etc/neo4j/neo4j.conf')
            content = config_file.content_string
            assert f'jmxremote.port={jmx_port}' in content


class TestNeo4jHighAvailability:
    """Test Neo4j high availability features"""

    def test_ha_scripts_exist(self, host):
        """Test that HA scripts exist when HA is enabled"""
        cluster_enabled = host.ansible.get_variables().get('neo4j_cluster_enabled', False)
        
        if cluster_enabled:
            cluster_monitor = host.file('/usr/local/bin/neo4j-cluster-monitor.sh')
            assert cluster_monitor.exists
            assert cluster_monitor.is_file
            assert cluster_monitor.mode == 0o755

    def test_haproxy_configuration(self, host):
        """Test HAProxy configuration when enabled"""
        ha_proxy_enabled = host.ansible.get_variables().get('neo4j_ha_proxy_enabled', False)
        
        if ha_proxy_enabled:
            haproxy_config = host.file('/etc/haproxy/conf.d/neo4j.cfg')
            assert haproxy_config.exists
            assert haproxy_config.is_file


class TestNeo4jServiceDependencies:
    """Test Neo4j service dependencies"""

    def test_systemd_overrides_exist(self, host):
        """Test that systemd override files exist when dependencies are configured"""
        depends_on = host.ansible.get_variables().get('neo4j_depends_on_services', [])
        
        if depends_on:
            override_dir = host.file('/etc/systemd/system/neo4j.service.d')
            assert override_dir.exists
            assert override_dir.is_directory
            
            timeout_conf = host.file('/etc/systemd/system/neo4j.service.d/timeout.conf')
            assert timeout_conf.exists

    def test_pre_start_check_script(self, host):
        """Test that pre-start check script exists"""
        pre_start_script = host.file('/usr/local/bin/neo4j-pre-start-check.sh')
        assert pre_start_script.exists
        assert pre_start_script.is_file
        assert pre_start_script.mode == 0o755


class TestNeo4jDataManagement:
    """Test Neo4j data import/export functionality"""

    def test_import_export_directories(self, host):
        """Test that import and export directories exist"""
        import_dir = host.file('/var/lib/neo4j/import')
        export_dir = host.file('/var/lib/neo4j/export')
        
        assert import_dir.exists
        assert import_dir.is_directory
        assert import_dir.user == 'neo4j'
        
        assert export_dir.exists
        assert export_dir.is_directory
        assert export_dir.user == 'neo4j'

    def test_export_script_exists(self, host):
        """Test that export script exists when scheduled exports are enabled"""
        export_scheduled = host.ansible.get_variables().get('neo4j_export_scheduled', False)
        
        if export_scheduled:
            export_script = host.file('/usr/local/bin/neo4j-export-backup.sh')
            assert export_script.exists
            assert export_script.is_file
            assert export_script.mode == 0o755
