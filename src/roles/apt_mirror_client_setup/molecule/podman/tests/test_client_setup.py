import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_sources_list(host):
    sources = host.file('/etc/apt/sources.list')
    assert sources.exists
    assert 'your-apt-mirror-url' in sources.content_string
