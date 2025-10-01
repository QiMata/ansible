# Kafka Broker Role

## Overview

The **kafka_broker** role installs Apache Kafka on Debian-based systems and configures it as a systemd service. It can be used for simple single-node setups or as part of a larger cluster with multiple brokers and ZooKeeper nodes.

## Supported Operating Systems/Platforms

- Debian 11/12
- Ubuntu 20.04/22.04

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `kafka_broker_version` | `"3.5.2"` | Kafka release to install |
| `kafka_broker_scala_version` | `"2.13"` | Scala version for binaries |
| `kafka_broker_install_dir` | `/opt/kafka` | Installation base directory |
| `kafka_broker_data_dir` | `/var/lib/kafka` | Directory for Kafka logs |
| `kafka_broker_user` | `kafka` | Service user |
| `kafka_broker_listeners` | `PLAINTEXT://0.0.0.0:9092` | Listener string |
| `kafka_broker_zookeeper_connect` | `localhost:2181` | ZooKeeper connection |

## Example Playbook

```yaml
- hosts: kafka_brokers
  become: true
  roles:
    - kafka_broker
```
