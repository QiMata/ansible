# OpenLDAP HAProxy Load Balancing Role

This role configures HAProxy for OpenLDAP load balancing and high availability, including connection pooling, health checks, and advanced traffic management.

## Features

- **Load Balancing**: Round-robin, least connections, and source IP persistence
- **Health Checks**: LDAP-specific health monitoring
- **Connection Pooling**: Efficient connection management
- **SSL Termination**: TLS offloading and certificate management
- **Failover**: Automatic failover to healthy LDAP servers
- **Monitoring**: Detailed metrics and alerting

## Requirements

- HAProxy 2.0 or higher
- OpenLDAP servers already configured
- SSL certificates for TLS termination (optional)

## Role Variables

### HAProxy Configuration
```yaml
openldap_haproxy_enabled: true
openldap_haproxy_version: "2.4"
openldap_haproxy_bind_address: "0.0.0.0"
openldap_haproxy_ldap_port: 389
openldap_haproxy_ldaps_port: 636
openldap_haproxy_stats_port: 8080
```

### Load Balancing
```yaml
openldap_haproxy_balance_method: "roundrobin"
openldap_haproxy_max_connections: 1000
openldap_haproxy_connection_timeout: 30
openldap_haproxy_server_timeout: 30
```

### LDAP Servers
```yaml
openldap_haproxy_servers:
  - name: "ldap1"
    address: "10.0.1.10"
    port: 389
    weight: 100
    check: true
  - name: "ldap2"
    address: "10.0.1.11"
    port: 389
    weight: 100
    check: true
```

## Dependencies

- `haproxy` package
- `openldap_server` role

## Example Playbook

```yaml
- hosts: haproxy_servers
  roles:
    - role: openldap_haproxy
      openldap_haproxy_servers:
        - name: "ldap-primary"
          address: "192.168.1.10"
          port: 389
          weight: 200
        - name: "ldap-secondary"
          address: "192.168.1.11"
          port: 389
          weight: 100
```

## Testing

Use Molecule for testing:

```bash
cd roles/security_identity/openldap/openldap_haproxy
molecule test
```
