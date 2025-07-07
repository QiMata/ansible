import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_backup_dir_exists(host):
    d = host.file('/var/backups/postgres')
    assert d.is_directory


def test_backup_script(host):
    f = host.file('/usr/local/bin/backup_postgres.sh')
    assert f.exists
    assert f.mode & 0o111


def test_systemd_units(host):
    svc = host.file('/etc/systemd/system/postgres_backup.service')
    timer = host.file('/etc/systemd/system/postgres_backup.timer')
    assert svc.exists
    assert timer.exists


def test_timer_enabled(host):
    timer = host.service('postgres_backup.timer')
    assert timer.is_enabled
