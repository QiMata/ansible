import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_kibana_package_installed(host):
    pkg = host.package("kibana")
    assert pkg.is_installed


def test_kibana_service_running_and_enabled(host):
    service = host.service("kibana")
    assert service.is_running
    assert service.is_enabled


def test_kibana_configuration_present(host):
    cfg = host.file("/etc/kibana/kibana.yml")
    assert cfg.exists
    assert cfg.user == "kibana"
    assert cfg.group == "kibana"
