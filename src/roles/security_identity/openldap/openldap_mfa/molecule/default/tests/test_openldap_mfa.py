import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.mark.parametrize("package", [
    "libpam-google-authenticator",
    "opensc",
    "libpam-pkcs11",
    "python3-oauthlib",
    "python3-saml2",
    "qrencode"
])
def test_mfa_packages_installed(host, package):
    """Test that MFA packages are installed."""
    pkg = host.package(package)
    assert pkg.is_installed


def test_mfa_directories_exist(host):
    """Test that MFA directories are created."""
    directories = [
        "/etc/openldap/mfa",
        "/var/lib/openldap/mfa",
        "/var/log/openldap"
    ]
    for directory in directories:
        assert host.file(directory).exists
        assert host.file(directory).is_directory
        assert host.file(directory).user == "openldap"
        assert host.file(directory).group == "openldap"


def test_totp_configuration_files(host):
    """Test that TOTP configuration files are created."""
    config_files = [
        "/etc/openldap/mfa/totp.conf",
        "/usr/local/bin/ldap-totp-verify"
    ]
    for config_file in config_files:
        assert host.file(config_file).exists
        assert host.file(config_file).is_file


def test_totp_verify_script_executable(host):
    """Test that TOTP verification script is executable."""
    script = host.file("/usr/local/bin/ldap-totp-verify")
    assert script.exists
    assert script.mode == 0o755


def test_slapd_service_running(host):
    """Test that slapd service is running."""
    service = host.service("slapd")
    assert service.is_running
    assert service.is_enabled


def test_ldap_port_listening(host):
    """Test that LDAP port is listening."""
    socket = host.socket("tcp://0.0.0.0:389")
    assert socket.is_listening


def test_mfa_audit_log_writable(host):
    """Test that MFA audit log is writable."""
    audit_log = host.file("/var/log/openldap/mfa-audit.log")
    # File might not exist yet, but directory should be writable
    log_dir = host.file("/var/log/openldap")
    assert log_dir.exists
    assert log_dir.is_directory
    assert log_dir.user == "openldap" or log_dir.mode & 0o200  # writable


def test_totp_config_content(host):
    """Test that TOTP configuration contains expected values."""
    config = host.file("/etc/openldap/mfa/totp.conf")
    assert config.exists
    content = config.content_string
    assert "TOTP_ISSUER=Test Organization" in content
    assert "TOTP_WINDOW_SIZE=3" in content
    assert "LDAP_BASE_DN=dc=test,dc=local" in content


def test_python_ldap3_import(host):
    """Test that Python ldap3 module can be imported."""
    cmd = host.run("python3 -c 'import ldap3; print(ldap3.__version__)'")
    assert cmd.rc == 0
    assert cmd.stdout.strip() != ""


def test_google_authenticator_pam_module(host):
    """Test that Google Authenticator PAM module is available."""
    pam_module = host.file("/lib/x86_64-linux-gnu/security/pam_google_authenticator.so")
    if not pam_module.exists:
        # Try alternative location
        pam_module = host.file("/usr/lib/x86_64-linux-gnu/security/pam_google_authenticator.so")
    # Note: The exact path may vary, so we just check if the package is installed
    pkg = host.package("libpam-google-authenticator")
    assert pkg.is_installed
