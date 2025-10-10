
def test_zookeeper_configuration(host):
    vars = host.ansible.get_variables()
    cfg_path = vars.get("zookeeper_config_path", "/etc/zookeeper/conf/zoo.cfg")
    cfg = host.file(cfg_path)
    assert cfg.exists
    assert cfg.user == "root"
    assert "clientPort={}".format(vars.get("zookeeper_client_port", 2181)) in cfg.content_string

    zookeeper_nodes = vars.get("zookeeper_nodes", [])
    peer_port = vars.get("zookeeper_peer_port", 2888)
    election_port = vars.get("zookeeper_leader_election_port", 3888)
    for idx, server in enumerate(zookeeper_nodes, 1):
        expected = f"server.{idx}={server}:{peer_port}:{election_port}"
        assert expected in cfg.content_string


def test_myid_matches_inventory(host):
    vars = host.ansible.get_variables()
    data_path = vars.get("zookeeper_myid_path", "/var/lib/zookeeper/myid")
    myid = host.file(data_path)
    assert myid.exists
    inventory_hostname = vars.get("inventory_hostname")
    zookeeper_nodes = vars.get("zookeeper_nodes", [])
    expected_id = str(zookeeper_nodes.index(inventory_hostname) + 1)
    assert myid.content_string.strip() == expected_id


def test_zookeeper_service_running(host):
    vars = host.ansible.get_variables()
    service_name = vars.get("zookeeper_service_name", "zookeeper")
    service = host.service(service_name)
    assert service.is_enabled
    assert service.is_running
