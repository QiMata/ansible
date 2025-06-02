import testinfra.utils.ansible_runner

def test_apache_airflow_cli(host):
    cmd = host.run("airflow version")
    assert cmd.rc == 0
