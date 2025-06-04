import os
import testinfra.utils.ansible_runner

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
