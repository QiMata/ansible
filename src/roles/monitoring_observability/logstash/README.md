# monitoring_observability.logstash

An Ansible role that installs and configures Logstash as part of an Elastic Stack deployment. The role bootstraps package repositories, installs Logstash, manages the primary configuration files, deploys pipeline definitions, and ensures the service is running.

## Requirements

- Supported operating systems: Debian 11/12, Ubuntu 20.04/22.04, and RHEL-compatible distributions with systemd.
- Network access to Elastic package repositories unless the repository configuration is overridden.

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `logstash_package` | Package name (or versioned package) to install. Override to pin versions. | `"logstash"` |
| `logstash_package_state` | Desired package state. | `present` |
| `logstash_repo_manage` | Whether to manage Elastic package repositories. | `true` |
| `logstash_major_version` | Elastic repository channel to use. | `"8.x"` |
| `logstash_settings` | Dictionary rendered into `logstash.yml`. | See defaults |
| `logstash_pipelines` | List rendered into `pipelines.yml`. | Single main pipeline |
| `logstash_pipeline_files` | List of pipeline configuration files to render under `conf.d`. | Beats to stdout example |
| `logstash_environment` | Dictionary of environment variables applied through a systemd override. | `{}` |
| `logstash_service_state` | Desired service state (`started`, `stopped`, etc.). | `started` |
| `logstash_service_enabled` | Enable Logstash on boot. | `true` |
| `logstash_extra_packages` | Additional packages to install alongside Logstash. | `[]` |
| `logstash_healthcheck_enabled` | Perform a simple HTTP health check after deployment. | `true` |
| `logstash_healthcheck_url` | URL used for the health check. | `http://127.0.0.1:9600/_node/pipelines` |

See `defaults/main.yml` for the full list of variables.

## Dependencies

None. Logstash integrates with Beats and Elasticsearch roles in this repository, but no hard dependencies are declared.

## Example Playbook

```yaml
- name: Deploy Logstash
  hosts: logstash_servers
  become: true
  roles:
    - role: monitoring_observability.logstash
      vars:
        logstash_pipeline_files:
          - name: beats.conf
            content: |
              input {
                beats { port => 5044 }
              }
              output {
                elasticsearch {
                  hosts => ["http://elasticsearch.internal:9200"]
                }
              }
```

## Molecule

The default Molecule scenario provisions Logstash on Debian 12 and verifies the service and configuration files via Testinfra.

## License

MIT

## Author

Example Inc.
