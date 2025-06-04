import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_airflow_cli(host):
    cmd = host.run('airflow version')
    assert cmd.rc == 0


def test_config_file(host):
    cfg = host.file('/opt/airflow/airflow.cfg')
    assert cfg.exists


def test_services_running(host):
    for svc in ['airflow-webserver', 'airflow-scheduler']:
        service = host.service(svc)
        assert service.is_enabled
        assert service.is_running
    assert host.socket('tcp://0.0.0.0:8080').is_listening
