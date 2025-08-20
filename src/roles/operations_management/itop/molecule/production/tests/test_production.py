"""
Production scenario tests for iTop role
Tests SSL, automated installation, and advanced monitoring features
"""

import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_ssl_certificates_exist(host):
    """Test that SSL certificates were generated"""
    ssl_cert = host.file('/etc/ssl/certs/itop.crt')
    ssl_key = host.file('/etc/ssl/private/itop.key')
    
    assert ssl_cert.exists
    assert ssl_cert.mode == 0o644
    assert ssl_key.exists
    assert ssl_key.mode == 0o600


def test_ssl_virtual_host(host):
    """Test SSL virtual host configuration"""
    vhost = host.file('/etc/apache2/sites-available/itop.conf')
    assert vhost.exists
    assert vhost.contains('SSLEngine on')
    assert vhost.contains('SSLCertificateFile /etc/ssl/certs/itop.crt')
    assert vhost.contains('SSLCertificateKeyFile /etc/ssl/private/itop.key')


def test_ssl_module_enabled(host):
    """Test that SSL module is enabled in Apache"""
    cmd = host.run("a2enmod -q ssl")
    assert cmd.rc == 0


def test_https_port_listening(host):
    """Test that Apache is listening on HTTPS port"""
    socket_https = host.socket('tcp://0.0.0.0:443')
    socket_http = host.socket('tcp://0.0.0.0:80')
    
    assert socket_https.is_listening
    assert socket_http.is_listening


def test_auto_install_completed(host):
    """Test that automated installation completed successfully"""
    config_file = host.file('/var/www/html/itop/conf/production/config-itop.php')
    assert config_file.exists
    assert config_file.user == 'www-data'
    assert config_file.group == 'www-data'


def test_itop_configuration_content(host):
    """Test iTop configuration file content"""
    config_file = host.file('/var/www/html/itop/conf/production/config-itop.php')
    if config_file.exists:
        content = config_file.content_string
        assert 'secure_test_password' in content
        assert 'production' in content


def test_unattended_install_response_removed(host):
    """Test that unattended install response file was cleaned up"""
    response_file = host.file('/var/www/html/itop/unattended_install.xml')
    assert not response_file.exists


def test_advanced_monitoring_features(host):
    """Test advanced monitoring features"""
    # Health check cron job
    cron_cmd = host.run("crontab -l")
    if cron_cmd.rc == 0:
        assert 'itop-health-check.sh' in cron_cmd.stdout
    
    # Health endpoint with JSON response
    health_php = host.file('/var/www/html/itop/health.php')
    assert health_php.exists
    assert health_php.contains('application/json')
    assert health_php.contains('database')
    assert health_php.contains('disk_usage')


def test_security_headers(host):
    """Test security headers in .htaccess"""
    htaccess = host.file('/var/www/html/itop/.htaccess')
    assert htaccess.exists
    assert htaccess.contains('X-Content-Type-Options nosniff')
    assert htaccess.contains('X-Frame-Options DENY')
    assert htaccess.contains('X-XSS-Protection')
    assert htaccess.contains('Strict-Transport-Security')


def test_php_performance_tuning(host):
    """Test PHP configuration for production"""
    php_ini_path = None
    possible_paths = [
        '/etc/php/8.1/apache2/php.ini',
        '/etc/php/8.2/apache2/php.ini',
        '/etc/php/7.4/apache2/php.ini'
    ]
    
    for path in possible_paths:
        if host.file(path).exists:
            php_ini_path = path
            break
    
    if php_ini_path:
        php_ini = host.file(php_ini_path)
        content = php_ini.content_string
        assert 'memory_limit = 1024M' in content
        assert 'max_execution_time = 600' in content
        assert 'upload_max_filesize = 100M' in content


def test_log_rotation_advanced(host):
    """Test advanced log rotation configuration"""
    logrotate = host.file('/etc/logrotate.d/itop')
    assert logrotate.exists
    assert logrotate.contains('rotate 30')
    assert logrotate.contains('compress')
    assert logrotate.contains('delaycompress')
    assert logrotate.contains('postrotate')


def test_php_info_diagnostic(host):
    """Test PHP info diagnostic file"""
    phpinfo = host.file('/var/www/html/itop/phpinfo.php')
    assert phpinfo.exists
    assert phpinfo.contains('PHP Version')
    assert phpinfo.contains('Memory Limit')
    assert phpinfo.contains('MySQL Extension')


def test_file_security_permissions(host):
    """Test enhanced file security permissions"""
    # Check config directory permissions
    config_dir = host.file('/var/www/html/itop/conf')
    assert config_dir.exists
    assert config_dir.user == 'www-data'
    assert config_dir.group == 'www-data'
    
    # Check that sensitive files are not world-readable
    if config_dir.exists:
        # Directory should not be world-readable
        assert not (config_dir.mode & 0o004)


def test_apache_modules_production(host):
    """Test that required Apache modules are enabled for production"""
    modules = ['ssl', 'rewrite', 'headers']
    
    for module in modules:
        cmd = host.run(f"apache2ctl -M | grep {module}")
        assert cmd.rc == 0


def test_no_ldap_in_production_test(host):
    """Test LDAP is not configured in this production test scenario"""
    config_file = host.file('/var/www/html/itop/conf/production/config-itop.php')
    if config_file.exists:
        content = config_file.content_string
        # Should not contain LDAP config since we disabled it in test
        assert 'ldap_host' not in content


def test_ssl_security_configuration(host):
    """Test SSL security configuration"""
    vhost = host.file('/etc/apache2/sites-available/itop.conf')
    if vhost.exists:
        content = vhost.content_string
        assert 'SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1' in content
        assert 'SSLHonorCipherOrder' in content


def test_production_mode_configuration(host):
    """Test that iTop is configured in production mode"""
    config_file = host.file('/var/www/html/itop/conf/production/config-itop.php')
    if config_file.exists:
        content = config_file.content_string
        assert 'production' in content


def test_database_production_connectivity(host):
    """Test database connectivity with production credentials"""
    cmd = host.run("mysql -u itop_user -psecure_test_password -e 'USE itop_db; SELECT 1 as test;'")
    assert cmd.rc == 0
    assert 'test' in cmd.stdout
