import os
from datetime import datetime, timedelta

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_no_upgrades(host):
    cmd = host.run('apt list --upgradeable')
    assert 'upgradable from' not in cmd.stdout


def test_recent_apt_update_stamp(host):
    stamp = host.file('/var/lib/apt/periodic/update-success-stamp')
    assert stamp.exists
    stamp_age = datetime.utcnow() - datetime.utcfromtimestamp(stamp.mtime)
    assert stamp_age < timedelta(hours=24)

