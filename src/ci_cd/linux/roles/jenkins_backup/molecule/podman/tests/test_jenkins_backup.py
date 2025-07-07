import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_backup_dir(host):
    d = host.file('/var/backups/jenkins')
    assert d.is_directory


def test_backup_file_exists(host):
    backups = host.run("ls /var/backups/jenkins/jenkins-*.tar.gz")
    assert backups.rc == 0
