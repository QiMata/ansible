"""
Enhanced iTop role tests using Testinfra
Tests all major components: installation, database, web server, monitoring
"""

import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_hosts_file(host):
    """Test that the hosts file exists"""
    f = host.file('/etc/hosts')
    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_itop_directory_exists(host):
    """Test that iTop directory exists with correct permissions"""
    itop_dir = host.file('/var/www/html/itop')
    assert itop_dir.exists
    assert itop_dir.is_directory
    assert itop_dir.user == 'www-data'
    assert itop_dir.group == 'www-data'


def test_itop_files_present(host):
    """Test that essential iTop files are present"""
    files = [
        '/var/www/html/itop/index.php',
        '/var/www/html/itop/application/application.inc.php'
    ]
    
    for file_path in files:
        f = host.file(file_path)
        assert f.exists
        assert f.user == 'www-data'
        assert f.group == 'www-data'


def test_database_exists(host):
    """Test that iTop database was created"""
    cmd = host.run("mysql -e 'SHOW DATABASES;' | grep itop_db")
    assert cmd.rc == 0
    assert 'itop_db' in cmd.stdout


def test_database_user_exists(host):
    """Test that iTop database user was created"""
    cmd = host.run("mysql -e \"SELECT User FROM mysql.user WHERE User='itop_user';\"")
    assert cmd.rc == 0
    assert 'itop_user' in cmd.stdout


def test_database_connectivity(host):
    """Test database connectivity with iTop user"""
    cmd = host.run("mysql -u itop_user -ptest_password -e 'USE itop_db; SHOW TABLES;'")
    assert cmd.rc == 0


def test_apache_service_running(host):
    """Test that Apache is running"""
    apache = host.service('apache2')
    assert apache.is_running
    assert apache.is_enabled


def test_mysql_service_running(host):
    """Test that MySQL is running"""
    mysql = host.service('mysql')
    assert mysql.is_running
    assert mysql.is_enabled


def test_apache_virtual_host(host):
    """Test Apache virtual host configuration"""
    vhost = host.file('/etc/apache2/sites-available/itop.conf')
    assert vhost.exists
    assert vhost.contains('DocumentRoot /var/www/html/itop')


def test_health_check_script(host):
    """Test monitoring health check script"""
    health_script = host.file('/usr/local/bin/itop-health-check.sh')
    assert health_script.exists
    assert health_script.mode == 0o755


def test_health_check_log(host):
    """Test health check log file"""
    log_file = host.file('/var/log/itop-health.log')
    assert log_file.exists
    assert log_file.user == 'www-data'


def test_logrotate_configuration(host):
    """Test log rotation configuration"""
    logrotate = host.file('/etc/logrotate.d/itop')
    assert logrotate.exists
    assert logrotate.contains('/var/log/itop-health.log')


def test_health_endpoint_exists(host):
    """Test health monitoring endpoint"""
    health_php = host.file('/var/www/html/itop/health.php')
    assert health_php.exists
    assert health_php.user == 'www-data'


def test_web_accessibility(host):
    """Test that Apache is listening on port 80"""
    socket = host.socket('tcp://0.0.0.0:80')
    assert socket.is_listening


def test_no_ssl_in_default(host):
    """Test that SSL is not configured in default scenario"""
    ssl_cert = host.file('/etc/ssl/certs/itop.crt')
    assert not ssl_cert.exists
