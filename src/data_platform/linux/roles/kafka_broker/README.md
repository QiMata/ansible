# Ansible Role: kafka_broker

This role installs and configures an Apache Kafka broker on Debian/Ubuntu hosts. It downloads the Kafka binaries, deploys a minimal `server.properties` configuration and sets up Kafka as a systemd service.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `kafka_broker_version` | `"3.5.2"` | Kafka version to install |
| `kafka_broker_scala_version` | `"2.13"` | Scala build of Kafka |
| `kafka_broker_install_dir` | `/opt/kafka` | Base installation directory |
| `kafka_broker_data_dir` | `/var/lib/kafka` | Data directory for logs |
| `kafka_broker_user` | `kafka` | User to run the service |
| `kafka_broker_group` | `kafka` | Group for the service |
| `kafka_broker_listeners` | `PLAINTEXT://0.0.0.0:9092` | Listener configuration |
| `kafka_broker_zookeeper_connect` | `localhost:2181` | ZooKeeper connection |

## Example Playbook

```yaml
- hosts: kafka_brokers
  become: true
  roles:
    - kafka_broker
```

The role assumes a ZooKeeper instance is reachable using `kafka_zookeeper_connect` unless you adapt the configuration for KRaft.
