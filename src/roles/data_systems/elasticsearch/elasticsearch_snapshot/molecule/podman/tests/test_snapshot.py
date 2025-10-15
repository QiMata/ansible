import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def test_snapshot_script(host):
    script = host.file('/usr/local/bin/elasticsearch_snapshot.sh')
    assert script.exists
    assert script.mode & 0o111

def test_cron_job(host):
    cron = host.check_output('crontab -l -u root')
    assert '/usr/local/bin/elasticsearch_snapshot.sh' in cron
