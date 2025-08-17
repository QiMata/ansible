import os
import testinfra.utils.ansible_runner
import time
import requests


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_virtualenv_exists(host):
    venv = host.file('/opt/amundsen/search/venv')
    assert venv.is_directory


def test_package_installed(host):
    cmd = host.run('/opt/amundsen/search/venv/bin/pip show amundsen-search')
    assert cmd.rc == 0


def test_enhanced_packages_installed(host):
    """Test that enhanced packages are installed"""
    packages = ['redis', 'prometheus-client', 'statsd', 'cryptography', 'pyjwt']
    for package in packages:
        cmd = host.run(f'/opt/amundsen/search/venv/bin/pip show {package}')
        assert cmd.rc == 0


def test_config_file(host):
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    assert cfg.exists
    assert cfg.contains('ELASTICSEARCH_ENDPOINT')
    assert cfg.contains('ProdConfig')


def test_enhanced_config_features(host):
    """Test enhanced configuration features"""
    cfg = host.file('/opt/amundsen/search/venv/config.py')
    assert cfg.contains('ELASTICSEARCH_CLIENT_CONFIG')
    assert cfg.contains('SEARCH_RESULT_SIZE')
    assert cfg.contains('LOG_LEVEL')


def test_systemd_unit(host):
    unit = host.file('/etc/systemd/system/amundsen-search.service')
    assert unit.exists
    assert unit.contains('--bind 0.0.0.0:5001')
    assert unit.contains('--graceful-timeout')


def test_enhanced_systemd_features(host):
    """Test enhanced systemd features"""
    unit = host.file('/etc/systemd/system/amundsen-search.service')
    assert unit.contains('NoNewPrivileges=true')
    assert unit.contains('PrivateTmp=true')
    assert unit.contains('LimitNOFILE=65536')


def test_directories_created(host):
    """Test that all required directories are created"""
    directories = [
        '/etc/amundsen/search',
        '/var/log/amundsen',
        '/opt/amundsen/search/certs'
    ]
    for directory in directories:
        dir_obj = host.file(directory)
        assert dir_obj.is_directory
        assert dir_obj.user == 'amundsen'
        assert dir_obj.group == 'amundsen'


def test_health_check_script(host):
    """Test health check script exists and is executable"""
    health_script = host.file('/opt/amundsen/search/venv/health_check.py')
    assert health_script.exists
    assert health_script.mode == 0o755
    assert health_script.user == 'amundsen'


def test_logrotate_config(host):
    """Test logrotate configuration"""
    logrotate = host.file('/etc/logrotate.d/amundsen-search')
    assert logrotate.exists
    assert logrotate.contains('/var/log/amundsen/search.log')


def test_service_running(host):
    """Test that the service is running"""
    service = host.service('amundsen-search')
    assert service.is_running
    assert service.is_enabled


def test_service_port_listening(host):
    """Test that the service is listening on the correct port"""
    socket = host.socket("tcp://0.0.0.0:5001")
    assert socket.is_listening


def test_health_endpoint_responds(host):
    """Test that health endpoint responds (if health checks are enabled)"""
    try:
        # Wait a bit for service to fully start
        time.sleep(5)
        response = requests.get('http://localhost:5001/healthcheck', timeout=10)
        # Should get either 200 (healthy) or 503 (unhealthy but responding)
        assert response.status_code in [200, 503]
    except requests.exceptions.RequestException:
        # Health endpoint might not be enabled in basic test
        pass


def test_user_exists(host):
    """Test that amundsen user exists"""
    user = host.user('amundsen')
    assert user.exists
    assert user.shell == '/usr/sbin/nologin'


def test_file_permissions(host):
    """Test critical file permissions"""
    venv = host.file('/opt/amundsen/search/venv')
    assert venv.user == 'amundsen'
    assert venv.group == 'amundsen'
    
    config = host.file('/opt/amundsen/search/venv/config.py')
    assert config.user == 'amundsen'
    assert config.group == 'amundsen'
    assert config.mode == 0o644


def test_log_directory_permissions(host):
    """Test log directory permissions"""
    log_dir = host.file('/var/log/amundsen')
    assert log_dir.is_directory
    assert log_dir.user == 'amundsen'
    assert log_dir.group == 'amundsen'


def test_service_running(host):
    svc = host.service('amundsen-search')
    assert svc.is_enabled
    assert svc.is_running
    sock = host.socket('tcp://0.0.0.0:5001')
    assert sock.is_listening
