# Filebeat Role Configuration Guide

This document provides comprehensive configuration examples and explanations for all features available in the enhanced Filebeat role.

## Table of Contents

1. [Basic Configuration](#basic-configuration)
2. [Input Configuration](#input-configuration)
3. [Output Configuration](#output-configuration)
4. [Security Configuration](#security-configuration)
5. [Processing and Enrichment](#processing-and-enrichment)
6. [Modules Configuration](#modules-configuration)
7. [Monitoring and Health Checks](#monitoring-and-health-checks)
8. [Performance Tuning](#performance-tuning)
9. [Operational Features](#operational-features)
10. [Advanced Examples](#advanced-examples)

## Basic Configuration

### Minimal Configuration

```yaml
filebeat_inputs:
  - type: log
    paths:
      - /var/log/app.log
    fields:
      service: myapp
```

### Global Configuration

```yaml
filebeat_environment: production
filebeat_global_tags:
  datacenter: us-east-1
  team: platform
filebeat_global_fields:
  region: america
  compliance: required
```

## Input Configuration

### Single Log File Input

```yaml
filebeat_inputs:
  - type: log
    id: app-logs
    enabled: true
    paths:
      - /var/log/myapp/*.log
    fields:
      service: myapp
      log_type: application
```

### Multiple Input Types

```yaml
filebeat_inputs:
  # Log files
  - type: log
    id: nginx-access
    paths:
      - /var/log/nginx/access.log*
    fields:
      service: nginx
      log_type: access
  
  # Journal logs (systemd)
  - type: journald
    id: systemd-logs
    enabled: true
  
  # Docker container logs
  - type: docker
    id: docker-logs
    enabled: true
    containers.ids: ["*"]
```

### Multiline Configuration

```yaml
filebeat_inputs:
  - type: log
    paths:
      - /var/log/java-app.log
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after
      max_lines: 500
      timeout: 5s
```

### Input-Level Processors

```yaml
filebeat_inputs:
  - type: log
    paths:
      - /var/log/nginx/access.log
    processors:
      - dissect:
          tokenizer: '%{clientip} %{ident} %{auth} [%{timestamp}] "%{verb} %{request} %{httpversion}" %{response} %{bytes}'
          field: "message"
      - convert:
          fields:
            - {from: "response", to: "http.response.status_code", type: "integer"}
            - {from: "bytes", to: "http.response.body.bytes", type: "integer"}
```

## Output Configuration

### Logstash Output

```yaml
filebeat_output_type: logstash
filebeat_logstash_hosts:
  - "logstash1.example.com:5044"
  - "logstash2.example.com:5044"
filebeat_logstash_worker: 2
filebeat_logstash_compression_level: 3
filebeat_logstash_bulk_max_size: 2048
```

### Elasticsearch Output

```yaml
filebeat_output_type: elasticsearch
filebeat_elasticsearch_hosts:
  - "https://es1.example.com:9200"
  - "https://es2.example.com:9200"
filebeat_elasticsearch_username: "filebeat_writer"
filebeat_elasticsearch_password: "{{ vault_es_password }}"
filebeat_elasticsearch_index: "logs-%{+yyyy.MM.dd}"
```

### Kafka Output

```yaml
filebeat_output_type: kafka
filebeat_kafka_hosts:
  - "kafka1.example.com:9092"
  - "kafka2.example.com:9092"
filebeat_kafka_topic: "logs"
filebeat_kafka_partition_round_robin:
  reachable_only: false
```

### File Output (for testing)

```yaml
filebeat_output_type: file
filebeat_file_path: "/tmp/filebeat"
filebeat_file_filename: "filebeat.json"
filebeat_file_rotate_every_kb: 10000
filebeat_file_number_of_files: 7
```

## Security Configuration

### SSL/TLS Configuration

```yaml
filebeat_ssl_enabled: true
filebeat_ssl_certificate: "/path/to/filebeat.crt"
filebeat_ssl_key: "/path/to/filebeat.key"
filebeat_ssl_certificate_authorities:
  - "/path/to/ca.crt"
filebeat_ssl_verification_mode: "full"  # full, strict, certificate, none
```

### API Key Authentication

```yaml
filebeat_api_key_enabled: true
filebeat_api_key_id: "{{ vault_api_key_id }}"
filebeat_api_key_value: "{{ vault_api_key_value }}"
```

### Username/Password Authentication

```yaml
filebeat_elasticsearch_username: "filebeat_user"
filebeat_elasticsearch_password: "{{ vault_password }}"
```

## Processing and Enrichment

### Global Processors

```yaml
filebeat_global_processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~
```

### Custom Processors

```yaml
filebeat_processors:
  - script:
      lang: javascript
      id: custom_processor
      source: >
        function process(event) {
          var msg = event.Get("message");
          if (msg && msg.includes("ERROR")) {
            event.Put("log.level", "error");
          }
        }
  
  - fingerprint:
      fields: ["message"]
      target_field: "message_fingerprint"
  
  - drop_event:
      when:
        regexp:
          message: "^$"  # Drop empty messages
```

## Modules Configuration

### Enable Modules

```yaml
filebeat_modules_enabled:
  - name: nginx
    config:
      access:
        enabled: true
        var:
          paths: ["/var/log/nginx/access.log*"]
      error:
        enabled: true
        var:
          paths: ["/var/log/nginx/error.log*"]
  
  - name: apache
    config:
      access:
        enabled: true
        var:
          paths: ["/var/log/apache2/access.log*"]
```

### Disable Modules

```yaml
filebeat_modules_disabled:
  - system
  - auditd
```

## Monitoring and Health Checks

### Basic Monitoring

```yaml
filebeat_monitoring_enabled: true
filebeat_health_check_enabled: true
filebeat_http_enabled: true
filebeat_http_host: "0.0.0.0"
filebeat_http_port: 5066
```

### Elasticsearch Monitoring

```yaml
filebeat_monitoring_enabled: true
filebeat_monitoring_elasticsearch_hosts:
  - "https://monitoring-es.example.com:9200"
filebeat_monitoring_elasticsearch_username: "monitoring_user"
filebeat_monitoring_elasticsearch_password: "{{ vault_monitoring_password }}"
```

## Performance Tuning

### Queue Configuration

```yaml
filebeat_queue_mem_events: 8192
filebeat_queue_mem_flush_min_events: 1024
filebeat_queue_mem_flush_timeout: 1s
```

### Harvester Settings

```yaml
filebeat_harvester_buffer_size: 32768
filebeat_harvester_max_bytes: 10485760  # 10MB
```

### Resource Limits

```yaml
filebeat_max_procs: 4  # 0 = use all available cores
```

## Operational Features

### Configuration Backup

```yaml
filebeat_config_backup_enabled: true
filebeat_config_backup_dir: "/etc/filebeat/backups"
filebeat_config_validate_before_restart: true
```

### Logging Configuration

```yaml
filebeat_logging_level: info
filebeat_logging_to_files: true
filebeat_logging_files_path: /var/log/filebeat
filebeat_logging_files_name: filebeat
filebeat_logging_files_keepfiles: 7
filebeat_logging_files_rotateeverybytes: 10485760
```

## Advanced Examples

### High-Volume Production Setup

```yaml
# Optimized for high-volume log processing
filebeat_inputs:
  - type: log
    id: high-volume-app
    paths:
      - /var/log/app/*.log
    harvester_buffer_size: 65536
    max_bytes: 52428800  # 50MB
    fields:
      service: high-volume-app

filebeat_output_type: elasticsearch
filebeat_elasticsearch_hosts:
  - "https://es-cluster.example.com:9200"

# Performance optimizations
filebeat_queue_mem_events: 16384
filebeat_queue_mem_flush_min_events: 2048
filebeat_logstash_bulk_max_size: 4096
filebeat_max_procs: 8

# Monitoring
filebeat_monitoring_enabled: true
filebeat_http_enabled: true
```

### Multi-Environment with Conditional Logic

```yaml
# Environment-specific configuration
filebeat_environment: "{{ env_name | default('production') }}"

# Conditional inputs based on environment
filebeat_inputs: >-
  {{
    (common_inputs | default([])) +
    (dev_inputs | default([]) if env_name == 'development' else []) +
    (prod_inputs | default([]) if env_name == 'production' else [])
  }}

# Conditional SSL
filebeat_ssl_enabled: "{{ env_name in ['production', 'staging'] }}"

# Environment-specific output
filebeat_output_type: "{{ 'file' if env_name == 'development' else 'elasticsearch' }}"
```

### Security-Hardened Configuration

```yaml
# Security-focused setup
filebeat_inputs:
  - type: log
    paths:
      - /var/log/audit/*.log
    fields:
      security_category: audit
      compliance: required

# Strict SSL
filebeat_ssl_enabled: true
filebeat_ssl_verification_mode: "strict"

# API key authentication
filebeat_api_key_enabled: true

# Security processors
filebeat_global_processors:
  - fingerprint:
      fields: ["message", "host.name", "@timestamp"]
      target_field: "security_hash"
  - script:
      lang: javascript
      source: |
        function process(event) {
          // Add security enrichment
          event.Put("security.processed_at", new Date().toISOString());
        }

# Enhanced monitoring
filebeat_monitoring_enabled: true
filebeat_health_check_enabled: true
```

## Variable Reference

For a complete list of all available variables, see `defaults/main.yml`. Key variable categories:

- **General**: `filebeat_version`, `filebeat_package_state`
- **Inputs**: `filebeat_inputs`, `filebeat_additional_inputs`
- **Outputs**: `filebeat_output_type`, `filebeat_*_hosts`
- **Security**: `filebeat_ssl_*`, `filebeat_api_key_*`
- **Processing**: `filebeat_processors`, `filebeat_global_processors`
- **Performance**: `filebeat_queue_*`, `filebeat_harvester_*`
- **Monitoring**: `filebeat_monitoring_*`, `filebeat_http_*`
- **Operational**: `filebeat_config_backup_*`, `filebeat_health_check_*`
