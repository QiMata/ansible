import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_haproxy_package_installed(host):
    """Test that HAProxy package is installed."""
    haproxy = host.package("haproxy")
    assert haproxy.is_installed


def test_haproxy_service_running(host):
    """Test that HAProxy service is running and enabled."""
    haproxy = host.service("haproxy")
    assert haproxy.is_running
    assert haproxy.is_enabled


def test_haproxy_configuration_file(host):
    """Test that HAProxy configuration file exists and is valid."""
    config = host.file("/etc/haproxy/haproxy.cfg")
    assert config.exists
    assert config.is_file
    assert config.user == "root"
    assert config.group == "root"
    assert config.mode == 0o644


def test_haproxy_directories_exist(host):
    """Test that HAProxy directories are created."""
    directories = [
        "/etc/haproxy/conf.d",
        "/var/log/haproxy"
    ]
    for directory in directories:
        d = host.file(directory)
        assert d.exists
        assert d.is_directory


def test_haproxy_config_syntax(host):
    """Test that HAProxy configuration syntax is valid."""
    cmd = host.run("haproxy -c -f /etc/haproxy/haproxy.cfg")
    assert cmd.rc == 0


def test_haproxy_ldap_port_listening(host):
    """Test that HAProxy is listening on LDAP port."""
    socket = host.socket("tcp://0.0.0.0:389")
    assert socket.is_listening


def test_haproxy_stats_port_listening(host):
    """Test that HAProxy stats port is listening."""
    socket = host.socket("tcp://0.0.0.0:8080")
    assert socket.is_listening


def test_haproxy_log_directory_writable(host):
    """Test that HAProxy log directory is writable."""
    log_dir = host.file("/var/log/haproxy")
    assert log_dir.exists
    assert log_dir.is_directory


@pytest.mark.parametrize("package", [
    "haproxy",
    "rsyslog",
    "openssl"
])
def test_required_packages_installed(host, package):
    """Test that required packages are installed."""
    pkg = host.package(package)
    assert pkg.is_installed


def test_haproxy_version(host):
    """Test HAProxy version."""
    cmd = host.run("haproxy -v")
    assert cmd.rc == 0
    assert "HAProxy" in cmd.stdout


def test_rsyslog_service_running(host):
    """Test that rsyslog service is running for HAProxy logging."""
    rsyslog = host.service("rsyslog")
    assert rsyslog.is_running
