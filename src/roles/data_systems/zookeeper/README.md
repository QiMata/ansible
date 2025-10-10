# data_systems.zookeeper

Install and configure an Apache ZooKeeper ensemble that can be shared by Apache NiFi and Apache Spark high-availability deployments. The role provisions the ZooKeeper packages, ensemble configuration, and service management on Debian, Ubuntu, and Enterprise Linux hosts.

## Requirements

* Supported operating systems: Debian 11/12, Ubuntu 20.04/22.04, and Enterprise Linux 8/9 families.
* The inventory must define the `zookeeper_nodes` variable with the list of inventory hostnames that participate in the ensemble.
* Passwordless SSH or appropriate privilege escalation to manage packages and services on the target nodes.

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `zookeeper_nodes` | Ordered list of inventory hostnames that form the ensemble. The index position determines the server ID (`myid`). | `[]` (must be overridden) |
| `zookeeper_client_port` | Client connection port. | `2181` |
| `zookeeper_peer_port` | Quorum peer port. | `2888` |
| `zookeeper_leader_election_port` | Leader election port. | `3888` |
| `zookeeper_data_dir` | Data directory for ZooKeeper snapshots and `myid`. | `/var/lib/zookeeper` |
| `zookeeper_log_dir` | Log directory for ZooKeeper. | `/var/log/zookeeper` |
| `zookeeper_tick_time` | Number of milliseconds of each tick. | `2000` |
| `zookeeper_init_limit` | Number of ticks for followers to connect and sync to leader. | `10` |
| `zookeeper_sync_limit` | Number of ticks that can pass between heartbeats. | `5` |
| `zookeeper_max_client_cnxns` | Maximum number of simultaneous client connections. | `60` |
| `zookeeper_autopurge_snap_retain_count` | Number of snapshots to retain in data directory. | `3` |
| `zookeeper_autopurge_purge_interval` | Hours between automatic purges. | `24` |
| `zookeeper_four_letter_word_whitelist` | Commands allowed for 4LW (four-letter word) operations. | `"*"` |
| `zookeeper_min_session_timeout` | Minimum session timeout in milliseconds. | `4000` |
| `zookeeper_max_session_timeout` | Maximum session timeout in milliseconds. | `40000` |
| `zookeeper_additional_properties` | Dictionary of extra ZooKeeper properties to merge into `zoo.cfg`. | `{}` |

## Inventory Example

```ini
[zookeeper_nodes]
zk1.example.com
zk2.example.com
zk3.example.com

[nifi_cluster]
nifi1.example.com
nifi2.example.com
nifi3.example.com

[spark_master]
spark-master.example.com

[spark_workers]
spark-worker-[1:3].example.com
```

Group variables (e.g., `group_vars/zookeeper_nodes.yml`):

```yaml
zookeeper_nodes:
  - zk1.example.com
  - zk2.example.com
  - zk3.example.com
zookeeper_client_port: 2181
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: zookeeper_nodes
  become: true
  roles:
    - role: data_systems/zookeeper
      vars:
        zookeeper_nodes: {{ groups['zookeeper_nodes'] }}
```

## Handlers

* `Restart ZooKeeper` – Restarts the ZooKeeper service when configuration files change.

## License

MIT
