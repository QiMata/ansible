# Kibana Role

This role installs and configures [Kibana](https://www.elastic.co/kibana) following the conventions used by the Elasticsearch role in this repository. It provisions the Elastic package repository, installs the Kibana package, renders `kibana.yml` from templated variables (including TLS), and ensures the systemd unit is enabled and running.

## Requirements

- Supported operating systems: Debian-based distributions (validated on Ubuntu 22.04 via Molecule).
- A reachable Elasticsearch cluster. The Molecule scenarios provision Elasticsearch on the same host using repository roles for integration testing.
- Network access to `artifacts.elastic.co` when `kibana_manage_repo` is `true`.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `kibana_version` | `"8.x"` | Elastic package channel used for installation. |
| `kibana_package_state` | `present` | Package state for Kibana. |
| `kibana_manage_repo` | `true` | Whether to configure the Elastic APT repository. |
| `kibana_service_state` | `started` | Desired Kibana service state. |
| `kibana_service_enabled` | `true` | Enable Kibana service on boot. |
| `kibana_server_host` | `"0.0.0.0"` | Bind host for Kibana HTTP service. |
| `kibana_server_port` | `5601` | Kibana HTTP port. |
| `kibana_elasticsearch_hosts` | `["http://localhost:9200"]` | List of Elasticsearch endpoints Kibana connects to. |
| `kibana_elasticsearch_username` | `""` | Optional username for Elasticsearch authentication. |
| `kibana_elasticsearch_password` | `""` | Optional password for Elasticsearch authentication. |
| `kibana_elasticsearch_ssl_verification_mode` | `full` | SSL verification mode (`none`, `certificate`, or `full`). |
| `kibana_enable_tls` | `false` | Enable HTTPS for Kibana. |
| `kibana_tls_*` | See defaults | TLS certificate, key, and CA paths/contents for Kibana. Provide file sources or inline PEM strings. |
| `kibana_elasticsearch_ssl_ca_*` | See defaults | Optional CA bundle for securing Kibana -> Elasticsearch traffic. |
| `kibana_reporting_enabled` | `false` | Toggle reporting features. |
| `kibana_monitoring_enabled` | `true` | Enable Kibana monitoring UI. |
| `kibana_fleet_enabled` | `true` | Enable Fleet and Integrations app. |
| `kibana_telemetry_enabled` | `false` | Control telemetry collection. |
| `kibana_extra_settings` | `{}` | Additional key/value pairs merged directly into `kibana.yml`. |

Refer to [`defaults/main.yml`](defaults/main.yml) for a complete list of variables.

### TLS Support

The role can manage TLS materials for both the Kibana HTTP server and its connection to Elasticsearch. Set `kibana_enable_tls: true` and provide certificate/key content or file sources. Optionally supply `kibana_elasticsearch_ssl_ca_src` or `kibana_elasticsearch_ssl_ca` to trust custom certificate authorities for upstream Elasticsearch clusters.

## Molecule Testing

Two Molecule scenarios validate the role:

- `molecule/default`: Uses the Docker driver (Podman compatible) to provision Elasticsearch and Kibana on Ubuntu 22.04. Verification ensures both services start, Kibana responds on the API, and status reflects connection to Elasticsearch.
- `molecule/proxmox`: Targets an external Proxmox VM via the shared automation harness. Verification asserts the Kibana service is running and healthy with Elasticsearch connectivity.

Execute `molecule test` from the desired scenario directory to run the full suite.

## Example Inventory

```ini
[kibana_servers]
kibana1 ansible_host=10.10.0.12
kibana2 ansible_host=10.10.0.13

[elk:children]
logstash_servers
elasticsearch_servers
kibana_servers
```

## Example Playbook

```yaml
- name: Deploy Kibana
  hosts: kibana_servers
  become: true
  roles:
    - role: data_systems/kibana
      vars:
        kibana_elasticsearch_hosts:
          - "https://elasticsearch1.internal:9200"
        kibana_elasticsearch_ssl_verification_mode: certificate
        kibana_elasticsearch_ssl_ca_src: files/elastic-ca.crt
        kibana_enable_tls: true
        kibana_tls_cert_src: files/kibana.crt
        kibana_tls_key_src: files/kibana.key
```

## Dependencies

No additional Galaxy collections are required; the role relies solely on built-in Ansible modules.
