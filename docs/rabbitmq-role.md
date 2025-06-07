# RabbitMQ Role

## Overview

The **RabbitMQ** role installs and configures RabbitMQ on Debian based systems. It can manage a single broker for development or join multiple nodes into a cluster for high availability. The role enables the management and Prometheus plugins and deploys a basic `rabbitmq.conf`.

## Supported Operating Systems/Platforms

- Debian 11/12
- Ubuntu 20.04/22.04

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `rabbitmq_port` | 5672 | AMQP listener port |
| `rabbitmq_management_port` | 15672 | Management UI port |
| `rabbitmq_prometheus_port` | 15692 | Prometheus metrics port |
| `rabbitmq_clustered` | `false` | Whether to join a cluster |
| `rabbitmq_cluster_master_node` | first host in `rabbitmq_cluster` group | Master node name |
| `rabbitmq_erlang_cookie` | empty | Erlang cookie string for clustering |
| `rabbitmq_cluster_partition_handling` | `pause_minority` | Partition handling mode |
| `rabbitmq_plugins` | `[rabbitmq_management, rabbitmq_prometheus]` | List of plugins to enable |

## Example Playbook

```yaml
- hosts: rabbitmq
  become: true
  vars:
    rabbitmq_clustered: true
    rabbitmq_cluster_master_node: "rmq1"
    rabbitmq_erlang_cookie: "SECRET"
  roles:
    - rabbitmq
```

The role assumes the Erlang cookie is supplied securely (e.g. via Ansible Vault). For multi-node clusters only the master node sets the HA policy.


