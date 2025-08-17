import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_web_root(host):
    d = host.file('/var/www/html/itop')
    assert d.is_directory
    assert d.user == 'www-data'


def test_index_present(host):
    f = host.file('/var/www/html/itop/index.php')
    assert f.exists


def test_database(host):
    cmd = host.run("mysql -uitop_user -pitop_password -e 'SHOW DATABASES LIKE \"itop_db\";'")
    assert cmd.rc == 0
    assert 'itop_db' in cmd.stdout
