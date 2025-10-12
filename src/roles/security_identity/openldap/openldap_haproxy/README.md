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
security_identity_openldap_haproxy_enabled: true
security_identity_openldap_haproxy_version: "2.4"
security_identity_openldap_haproxy_bind_address: "0.0.0.0"
security_identity_openldap_haproxy_ldap_port: 389
security_identity_openldap_haproxy_ldaps_port: 636
security_identity_openldap_haproxy_stats_port: 8080
```

### Load Balancing
```yaml
security_identity_openldap_haproxy_balance_method: "roundrobin"
security_identity_openldap_haproxy_max_connections: 1000
security_identity_openldap_haproxy_connection_timeout: 30
security_identity_openldap_haproxy_server_timeout: 30
```

### LDAP Servers
```yaml
security_identity_openldap_haproxy_servers:
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

### SSL Termination
```yaml
security_identity_openldap_haproxy_ssl_enabled: false
security_identity_openldap_haproxy_ssl_certificate_dir: "/etc/ssl/certs"
security_identity_openldap_haproxy_ssl_dhparam_dir: "/etc/ssl/private"
security_identity_openldap_haproxy_ssl_certificate: "{{ security_identity_openldap_haproxy_ssl_certificate_dir }}/ldap.pem"
security_identity_openldap_haproxy_ssl_dhparam: "{{ security_identity_openldap_haproxy_ssl_dhparam_dir }}/dhparam.pem"
```

## Dependencies

- `haproxy` package
- `openldap_server` role

## Example Playbook

```yaml
- hosts: haproxy_servers
  roles:
    - role: openldap_haproxy
      security_identity_openldap_haproxy_servers:
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
