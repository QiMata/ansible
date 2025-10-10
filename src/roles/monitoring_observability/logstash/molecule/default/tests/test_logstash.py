import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_logstash_package_installed(host):
    pkg = host.package("logstash")
    assert pkg.is_installed


def test_logstash_service_running_and_enabled(host):
    service = host.service("logstash")
    assert service.is_running
    assert service.is_enabled


def test_logstash_configuration_files(host):
    for path in ["/etc/logstash/logstash.yml", "/etc/logstash/pipelines.yml"]:
        cfg = host.file(path)
        assert cfg.exists
        assert cfg.user == "logstash"
        assert cfg.group == "logstash"
