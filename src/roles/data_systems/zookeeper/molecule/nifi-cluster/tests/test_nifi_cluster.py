
def test_zookeeper_ensemble_configured(host):
    vars = host.ansible.get_variables()
    cfg_path = vars.get("zookeeper_config_path", "/etc/zookeeper/conf/zoo.cfg")
    cfg = host.file(cfg_path)
    assert cfg.exists
    assert "clientPort={}".format(vars.get("zookeeper_client_port", 2181)) in cfg.content_string


def test_zookeeper_service_active(host):
    vars = host.ansible.get_variables()
    service_name = vars.get("zookeeper_service_name", "zookeeper")
    service = host.service(service_name)
    assert service.is_enabled
    assert service.is_running
