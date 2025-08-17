import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_packages_installed(host):
    assert host.package('openjdk-17-jdk').is_installed


def test_user_exists(host):
    u = host.user('spark')
    assert u.exists


def test_install_dir(host):
    d = host.file('/opt/spark/current')
    assert d.is_directory


def test_master_service(host):
    svc = host.service('spark-master')
    assert svc.is_enabled
    assert svc.is_running


def test_worker_service(host):
    svc = host.service('spark-worker')
    assert svc.is_enabled
    assert svc.is_running


def test_history_service(host):
    svc = host.service('spark-history-server')
    assert svc.is_enabled
    assert svc.is_running


def test_ports(host):
    assert host.socket('tcp://0.0.0.0:7077').is_listening
    assert host.socket('tcp://0.0.0.0:8080').is_listening
    assert host.socket('tcp://0.0.0.0:8081').is_listening
    assert host.socket('tcp://0.0.0.0:18080').is_listening


def test_config_files(host):
    defaults = host.file('/opt/spark/current/conf/spark-defaults.conf')
    env = host.file('/opt/spark/current/conf/spark-env.sh')
    assert defaults.contains('spark.eventLog.enabled true')
    assert defaults.contains('/var/spark-events')
    assert env.contains('SPARK_WORKER_MEMORY')

