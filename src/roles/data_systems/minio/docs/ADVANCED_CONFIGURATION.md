# MinIO Advanced Configuration Examples

This document provides examples and best practices for configuring the advanced features of the MinIO role.

## Table of Contents

1. [Clustering Configuration](#clustering-configuration)
2. [Security and TLS](#security-and-tls)
3. [User and Access Management](#user-and-access-management)
4. [Monitoring and Observability](#monitoring-and-observability)
5. [Backup and Recovery](#backup-and-recovery)
6. [Network Security](#network-security)
7. [Production Best Practices](#production-best-practices)

## Clustering Configuration

### Basic 4-Node Cluster

```yaml
minio_enable_clustering: true
minio_cluster_nodes:
  - "minio1.example.com:9000"
  - "minio2.example.com:9000"
  - "minio3.example.com:9000"
  - "minio4.example.com:9000"
minio_cluster_drive_count: 4
minio_cluster_parity_drives: 2
```

### Multi-Drive Single Node

```yaml
minio_enable_clustering: false
minio_multiple_drives:
  - "/mnt/disk1"
  - "/mnt/disk2"
  - "/mnt/disk3"
  - "/mnt/disk4"
```

### Large Scale Cluster (8 Nodes)

```yaml
minio_enable_clustering: true
minio_cluster_node_count: 8
minio_cluster_drive_count: 8
minio_cluster_parity_drives: 4
minio_cluster_nodes:
  - "minio1.example.com:9000"
  - "minio2.example.com:9000"
  - "minio3.example.com:9000"
  - "minio4.example.com:9000"
  - "minio5.example.com:9000"
  - "minio6.example.com:9000"
  - "minio7.example.com:9000"
  - "minio8.example.com:9000"
```

## Security and TLS

### Let's Encrypt SSL Configuration

```yaml
minio_enable_tls: true
minio_enable_letsencrypt: true
minio_letsencrypt_email: "admin@example.com"
minio_letsencrypt_domains:
  - "minio.example.com"
  - "s3.example.com"
```

### Custom Certificate Configuration

```yaml
minio_enable_tls: true
minio_cert_public: "/path/to/certificate.crt"
minio_cert_private: "/path/to/private.key"
minio_ca_bundle_path: "/path/to/ca-bundle.crt"
```

### Client Certificate Authentication

```yaml
minio_enable_tls: true
minio_enable_client_certs: true
minio_tls_ciphers: "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256"
```

## User and Access Management

### Comprehensive User Setup

```yaml
minio_create_buckets:
  - name: "production-data"
    versioning: true
  - name: "staging-data"
    versioning: false
  - name: "backups"
    versioning: true

minio_create_users:
  - username: "production-app"
    password: "{{ vault_prod_app_password }}"
  - username: "staging-app"
    password: "{{ vault_staging_app_password }}"
  - username: "backup-service"
    password: "{{ vault_backup_password }}"

minio_bucket_policies:
  - name: "production-read-write"
    policy:
      Version: "2012-10-17"
      Statement:
        - Effect: "Allow"
          Principal: "*"
          Action:
            - "s3:GetObject"
            - "s3:PutObject"
            - "s3:DeleteObject"
          Resource: "arn:aws:s3:::production-data/*"
  - name: "backup-read-only"
    policy:
      Version: "2012-10-17"
      Statement:
        - Effect: "Allow"
          Principal: "*"
          Action: "s3:GetObject"
          Resource: "arn:aws:s3:::backups/*"

minio_service_accounts:
  - parent_user: "production-app"
    access_key: "{{ vault_prod_access_key }}"
    secret_key: "{{ vault_prod_secret_key }}"
  - parent_user: "backup-service"
    access_key: "{{ vault_backup_access_key }}"
    secret_key: "{{ vault_backup_secret_key }}"
```

### Access Key Rotation

```yaml
minio_access_key_rotation_days: 90  # Rotate every 90 days
```

## Monitoring and Observability

### Full Monitoring Stack

```yaml
minio_enable_prometheus: true
minio_prometheus_port: 9090
minio_enable_health_checks: true
minio_health_check_interval: "30s"
minio_enable_audit_logging: true
minio_audit_log_path: "/var/log/minio/audit.log"
minio_log_level: "INFO"
minio_disk_usage_threshold: 85
```

### Development Monitoring

```yaml
minio_enable_prometheus: true
minio_enable_health_checks: true
minio_log_level: "DEBUG"
minio_disk_usage_threshold: 90
```

## Backup and Recovery

### Comprehensive Backup Configuration

```yaml
minio_enable_backup: true
minio_backup_schedule: "0 2 * * *"  # Daily at 2 AM
minio_backup_retention_days: 30
minio_backup_destination: "s3://backup-bucket/minio-backups"

minio_enable_replication: true
minio_replication_targets:
  - source_bucket: "production-data"
    target_url: "https://dr-minio.example.com"
    target_bucket: "production-data-replica"
    region: "us-west-2"
  - source_bucket: "staging-data"
    target_url: "https://backup-minio.example.com"
    region: "us-east-1"
```

### Local Backup Only

```yaml
minio_enable_backup: true
minio_backup_schedule: "0 3 * * 0"  # Weekly on Sunday
minio_backup_retention_days: 90
minio_backup_destination: "/backup/minio"
```

## Network Security

### Firewall and Rate Limiting

```yaml
minio_enable_firewall: true
minio_allowed_ips:
  - "10.0.0.0/8"
  - "192.168.1.0/24"
  - "172.16.0.0/12"

minio_rate_limit_enabled: true
minio_rate_limit_requests: 1000  # requests per minute

minio_bind_address: "0.0.0.0"
```

### Reverse Proxy Configuration

```yaml
minio_enable_reverse_proxy: true
minio_reverse_proxy_config:
  type: "nginx"
  upstream_servers:
    - "minio1.example.com:9000"
    - "minio2.example.com:9000"
  ssl_certificate: "/etc/ssl/certs/minio.crt"
  ssl_certificate_key: "/etc/ssl/private/minio.key"
```

## Production Best Practices

### High Availability Production Setup

```yaml
# Clustering
minio_enable_clustering: true
minio_cluster_node_count: 4
minio_cluster_drive_count: 4
minio_cluster_parity_drives: 2

# Security
minio_enable_tls: true
minio_enable_letsencrypt: true
minio_enable_firewall: true
minio_rate_limit_enabled: true

# Monitoring
minio_enable_prometheus: true
minio_enable_health_checks: true
minio_enable_audit_logging: true

# Backup
minio_enable_backup: true
minio_enable_replication: true

# Storage
minio_storage_class: "STANDARD"
minio_enable_versioning: true
minio_disk_usage_threshold: 80

# Performance
minio_rate_limit_requests: 2000
minio_log_level: "WARN"
```

### Development Environment

```yaml
# Basic setup
minio_enable_clustering: false
minio_enable_tls: false

# Monitoring
minio_enable_health_checks: true
minio_enable_prometheus: true
minio_log_level: "DEBUG"

# Storage
minio_disk_usage_threshold: 95
minio_enable_versioning: false

# Simple user setup
minio_create_buckets:
  - name: "dev-data"
  - name: "test-uploads"
```

### Security Hardening Checklist

- ✅ Enable TLS with proper certificates
- ✅ Use strong, unique passwords stored in Ansible Vault
- ✅ Configure firewall rules to restrict access
- ✅ Enable audit logging
- ✅ Set up access key rotation
- ✅ Use principle of least privilege for user policies
- ✅ Enable rate limiting
- ✅ Configure fail2ban for intrusion detection
- ✅ Regular security audits with network security audit script

### Performance Optimization

- ✅ Use multiple drives per node for better I/O performance
- ✅ Configure appropriate erasure coding ratios
- ✅ Set up monitoring to track performance metrics
- ✅ Use SSD storage for better performance
- ✅ Configure network bonding for higher throughput
- ✅ Tune disk usage thresholds based on workload

### Disaster Recovery Planning

- ✅ Set up cross-region replication
- ✅ Regular backup testing and verification
- ✅ Document recovery procedures
- ✅ Test failover scenarios
- ✅ Monitor replication lag and backup success
- ✅ Maintain updated disaster recovery runbooks
