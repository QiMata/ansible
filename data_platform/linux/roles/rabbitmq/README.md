# Ansible Role: RabbitMQ

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Tags](#tags)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Testing Instructions](#testing-instructions)
* [Known Issues and Gotchas](#known-issues-and-gotchas)
* [Security Implications](#security-implications)
* [Cross-Referencing](#cross-referencing)

## Overview

This role installs **RabbitMQ** from the official packagecloud repository, configures `rabbitmq.conf`, and manages enabled plugins. It can optionally join a cluster when `rabbitmq_clustered` is `true`.

## Supported Operating Systems/Platforms

The role targets Debian-based systems and is tested on:

* **Debian 11** (Bullseye) and **Debian 12** (Bookworm)
* **Ubuntu 20.04 LTS** (Focal) and **Ubuntu 22.04 LTS** (Jammy)

## Role Variables

Default values from `defaults/main.yml`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `rabbitmq_port` | `5672` | AMQP port |
| `rabbitmq_management_port` | `15672` | Management UI port |
| `rabbitmq_prometheus_port` | `15692` | Prometheus plugin port |
| `rabbitmq_clustered` | `false` | Whether to join a cluster |
| `rabbitmq_cluster_master_node` | `{{ groups['rabbitmq_cluster'][0] | default(inventory_hostname) }}` | Cluster master hostname |
| `rabbitmq_erlang_cookie` | `""` | Erlang cookie used for clustering |
| `rabbitmq_cluster_partition_handling` | `"pause_minority"` | Partition handling policy |
| `rabbitmq_plugins` | `[rabbitmq_management, rabbitmq_prometheus]` | Plugins to enable |

## Tags

This role defines no internal tags. All tasks run whenever the role is applied.

## Dependencies

*Requires the* **community.general** *collection for package and service modules.*

## Example Playbook

```yaml
- hosts: rabbitmq
  become: true
  roles:
    - role: rabbitmq
      vars:
        rabbitmq_clustered: true
        rabbitmq_cluster_master_node: "rabbit1"
        rabbitmq_erlang_cookie: "supersecretcookie"
```

This example installs RabbitMQ on all hosts in the `rabbitmq` group and forms a cluster with node `rabbit1` as master.

## Testing Instructions

Use **Molecule** with the Docker driver to test the role in a container:

1. Install Molecule and Docker, e.g. `pip install molecule[docker]`.
2. From the role directory, run `molecule test` (or `create`/`converge`/`destroy` individually) to verify idempotence and configuration.

## Known Issues and Gotchas

* The role assumes internet access to reach packagecloud.io. Provide an internal mirror or local packages if your environment lacks direct access.
* Clustering requires the same Erlang cookie on all nodes and proper host name resolution between cluster members.

## Security Implications

RabbitMQ runs as its own system service account. Ensure network access to the AMQP and management ports is restricted to trusted clients. When clustering, nodes must communicate over the Erlang port range and share the secret cookie, so protect it with Ansible Vault or similar methods.

## Cross-Referencing

Other roles in this repository that may be used alongside RabbitMQ include **haproxy** for load balancing and **monitoring/prometheus** for metrics collection.
