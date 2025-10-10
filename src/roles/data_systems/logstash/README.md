# Logstash Role

This role installs and configures [Logstash](https://www.elastic.co/logstash) as part of the data systems stack. It provisions the Elastic package repository, installs the Logstash service, manages Beats input pipelines, optionally enables TLS, and ensures the systemd unit is enabled and running. The role follows the conventions used by the Elasticsearch role in this repository.

## Requirements

- Supported operating systems: Debian-based distributions (tested on Ubuntu 22.04 via Molecule).
- Network access to `artifacts.elastic.co` when `logstash_manage_repo` is `true`.
- Java runtime is provided by the Logstash package; no external dependency is required.

## Role Variables

| Variable | Default | Description |
| --- | --- | --- |
| `logstash_version` | `"8.x"` | Elastic package channel to install from. |
| `logstash_package_state` | `present` | Package state passed to `ansible.builtin.apt`. |
| `logstash_manage_repo` | `true` | Whether to configure the Elastic APT repository. |
| `logstash_service_state` | `started` | Desired state of the Logstash service. |
| `logstash_service_enabled` | `true` | Whether Logstash should start on boot. |
| `logstash_http_host` | `"0.0.0.0"` | Host/interface for the Logstash HTTP API. |
| `logstash_http_port` | `9600` | Port for the Logstash HTTP API. |
| `logstash_beats_host` | `"0.0.0.0"` | Host/interface for the Beats input plugin. |
| `logstash_beats_port` | `5044` | Port for Beats input. |
| `logstash_additional_inputs` | `[]` | List of extra input blocks (rendered verbatim) to include in the pipeline. |
| `logstash_filters` | `[]` | List of filter blocks (rendered verbatim). |
| `logstash_elasticsearch_hosts` | `["http://localhost:9200"]` | Hosts used by the default Elasticsearch output when no custom outputs are supplied. |
| `logstash_outputs` | `[]` | List of output blocks (rendered verbatim). |
| `logstash_enable_tls` | `false` | Enable TLS for Beats input and HTTP API. |
| `logstash_tls_*` | See defaults | Paths and content for TLS assets. You can provide `*_src` (file path) or inline content via `logstash_tls_cert`, `logstash_tls_key`, and `logstash_tls_ca`. |
| `logstash_heap_size` | `"1g"` | JVM heap size applied to both `-Xms` and `-Xmx`. |
| `logstash_jvm_options_extra` | `[]` | Additional JVM options written to `jvm.options.d/99-extra.options`. |
| `logstash_config_test` | `true` | Run `logstash --config.test_and_exit` before managing the service. |

See [`defaults/main.yml`](defaults/main.yml) for the full list of variables.

### TLS Support

When `logstash_enable_tls` is `true`, the role ensures the certificate directory exists and deploys TLS materials. Provide either controller-side file paths (`logstash_tls_cert_src`, etc.) or inline PEM contents (`logstash_tls_cert`, etc.). The Beats input will require TLS by default in this mode, and the HTTP API will expose TLS endpoints using the provided certificate and CA chain.

## Molecule Testing

Two Molecule scenarios are provided:

- `molecule/default`: Uses the Docker driver (Podman compatible) to converge Logstash on Ubuntu 22.04 and validates package installation, service state, HTTP API health, and Beats pipeline registration.
- `molecule/proxmox`: Reuses the Proxmox automation harness shared in this repository to converge Logstash on a remote VM. Verification ensures the service is active and the API reports the Beats pipeline.

Run tests with `molecule test` inside the desired scenario directory.

## Example Inventory

```ini
[logstash_servers]
logstash1 ansible_host=10.10.0.10
logstash2 ansible_host=10.10.0.11

[elk:children]
logstash_servers
elasticsearch_servers
kibana_servers
```

## Example Playbook

```yaml
- name: Deploy Logstash cluster
  hosts: logstash_servers
  become: true
  roles:
    - role: data_systems/logstash
      vars:
        logstash_elasticsearch_hosts:
          - "https://elasticsearch1.internal:9200"
        logstash_enable_tls: true
        logstash_tls_cert_src: files/logstash.crt
        logstash_tls_key_src: files/logstash.key
        logstash_tls_ca_src: files/ca.crt
```

## Dependencies

This role relies only on built-in Ansible modules. No additional Galaxy collections are required.
