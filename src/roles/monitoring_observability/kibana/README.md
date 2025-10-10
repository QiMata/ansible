# monitoring_observability.kibana

An Ansible role that installs and configures Kibana for Elastic Stack deployments. It sets up the Elastic package repositories, installs Kibana, manages the primary configuration file, and ensures the service is started and enabled. Optional health checks and systemd environment overrides are also supported.

## Requirements

- Supported operating systems: Debian 11/12, Ubuntu 20.04/22.04, Red Hat Enterprise Linux compatible distributions with systemd.
- Network access to Elastic package repositories unless you override the repository configuration.

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `kibana_package` | Package name (or versioned package) to install. Override to pin specific versions. | `"kibana"` |
| `kibana_package_state` | Desired package state. | `present` |
| `kibana_repo_manage` | Whether to configure the Elastic package repositories. | `true` |
| `kibana_major_version` | Elastic repository channel to use. | `"8.x"` |
| `kibana_config` | Dictionary rendered into `kibana.yml`. | See defaults |
| `kibana_environment` | Dictionary of environment variables applied through a systemd override. | `{}` |
| `kibana_service_state` | Desired service state (`started`, `stopped`, etc.). | `started` |
| `kibana_service_enabled` | Enable Kibana service on boot. | `true` |
| `kibana_extra_packages` | Additional packages to install alongside Kibana. | `[]` |
| `kibana_healthcheck_enabled` | Perform a simple HTTP health check after deployment. | `true` |
| `kibana_healthcheck_url` | URL used for the health check. | `http://127.0.0.1:5601/api/status` |

See `defaults/main.yml` for the full list of tunables.

## Dependencies

None. The role can be combined with the existing `data_systems.elasticsearch_install` role to provision Elasticsearch prior to Kibana when running Molecule or real deployments.

## Example Playbook

```yaml
- name: Deploy Kibana
  hosts: kibana_servers
  become: true
  roles:
    - role: data_systems.elasticsearch_install
    - role: monitoring_observability.kibana
      vars:
        kibana_config:
          server.host: "0.0.0.0"
          elasticsearch.hosts:
            - "https://elasticsearch.internal:9200"
```

## Molecule

A Molecule scenario is provided under `molecule/default` to verify installation on Debian-based systems.

## License

MIT

## Author

Example Inc.
