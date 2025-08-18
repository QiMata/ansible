# HAProxy Role Migration Guide

This guide helps you migrate from the basic HAProxy role to the new advanced version with enterprise features.

## Backward Compatibility

The new role maintains **100% backward compatibility** with existing configurations. All your current variables will continue to work without changes.

### Existing Variables (No Changes Required)

These variables work exactly as before:

```yaml
haproxy_package_name: haproxy
haproxy_service_name: haproxy
haproxy_frontend_name: hafrontend
haproxy_frontend_bind_address: "*"
haproxy_frontend_port: 80
haproxy_frontend_mode: "http"
haproxy_backend_name: habackend
haproxy_backend_mode: "http"
haproxy_backend_balance_method: "roundrobin"
haproxy_backend_httpchk: ""
haproxy_backend_servers: []
haproxy_ssl_certificate: ""
haproxy_ssl_certificate_content: ""
haproxy_stats_enable: false
haproxy_stats_user: admin
haproxy_stats_password: admin
haproxy_stats_port: 9000
haproxy_stats_bind_address: "127.0.0.1"
```

## Migration Scenarios

### Scenario 1: No Changes Needed

If you're happy with your current setup, you don't need to change anything. The role will generate the same configuration as before.

### Scenario 2: Gradual Migration to Advanced Features

You can gradually adopt new features without changing your existing configuration:

#### Step 1: Enable Basic Security Features

```yaml
# Add these to your existing variables
haproxy_security:
  hide_version: true
  server_tokens: false

haproxy_ssl_redirect:
  enable: true  # If you have SSL certificate
```

#### Step 2: Add Rate Limiting

```yaml
haproxy_rate_limiting:
  enable: true
  http_req_rate: 50
  http_req_burst: 100
```

#### Step 3: Enable Compression

```yaml
haproxy_compression:
  enable: true
```

#### Step 4: Add Monitoring

```yaml
haproxy_stats_enable: true
haproxy_prometheus:
  enable: true
```

### Scenario 3: Full Migration to New Structure

To use multiple frontends/backends, migrate your configuration:

#### Before (Legacy Format)
```yaml
haproxy_frontend_name: web_frontend
haproxy_frontend_port: 80
haproxy_backend_name: web_backend
haproxy_backend_servers:
  - name: web1
    address: "192.168.1.10:80"
  - name: web2
    address: "192.168.1.11:80"
```

#### After (New Format)
```yaml
haproxy_frontends:
  - name: web_frontend
    port: 80
    default_backend: web_backend

haproxy_backends:
  - name: web_backend
    servers:
      - name: web1
        address: "192.168.1.10:80"
      - name: web2
        address: "192.168.1.11:80"

# Keep legacy variables for compatibility
haproxy_frontend_name: web_frontend
haproxy_frontend_port: 80
haproxy_backend_name: web_backend
haproxy_backend_servers:
  - name: web1
    address: "192.168.1.10:80"
  - name: web2
    address: "192.168.1.11:80"
```

## New Features You Can Add

### Multiple Services

```yaml
haproxy_frontends:
  - name: web_frontend
    port: 80
    default_backend: web_backend
  - name: api_frontend
    port: 8080
    default_backend: api_backend

haproxy_backends:
  - name: web_backend
    servers:
      - name: web1
        address: "192.168.1.10:80"
  - name: api_backend
    servers:
      - name: api1
        address: "192.168.1.20:8080"
```

### SSL/TLS Enhancement

```yaml
haproxy_ssl_certificates:
  - path: "/etc/haproxy/certs/example.com.pem"
    content: "{{ vault_ssl_cert }}"

haproxy_hsts:
  enable: true
  max_age: 31536000

haproxy_ssl_redirect:
  enable: true
```

### Content Switching

```yaml
haproxy_acls:
  - name: "is_api"
    condition: "path_beg /api/"
  - name: "is_admin"
    condition: "path_beg /admin/"

haproxy_use_backends:
  - condition: "is_api"
    backend: "api_backend"
  - condition: "is_admin"
    backend: "admin_backend"
```

## Testing Your Migration

1. **Test in development first**
2. **Use configuration validation**:
   ```yaml
   haproxy_config_validation:
     enable: true
     backup_config: true
   ```
3. **Enable zero-downtime deployments**:
   ```yaml
   haproxy_zero_downtime:
     enable: true
   ```

## Common Issues and Solutions

### Issue: Configuration validation fails
**Solution**: Check for syntax errors in ACLs or backend definitions

### Issue: SSL redirect not working
**Solution**: Ensure both HTTP (80) and HTTPS (443) frontends are defined

### Issue: Rate limiting too aggressive
**Solution**: Adjust `http_req_rate` and `http_req_burst` values

### Issue: Prometheus metrics not available
**Solution**: Install `prometheus-haproxy-exporter` package manually if auto-install fails

## Rollback Plan

If you need to rollback:

1. **Disable new features**:
   ```yaml
   haproxy_frontends: []
   haproxy_backends: []
   haproxy_rate_limiting:
     enable: false
   haproxy_compression:
     enable: false
   ```

2. **Use backup configuration**:
   ```bash
   sudo cp /etc/haproxy/haproxy.cfg.backup /etc/haproxy/haproxy.cfg
   sudo systemctl reload haproxy
   ```

3. **Revert to legacy variables only**

## Support

For issues or questions about migration:

1. Check the logs: `journalctl -u haproxy -f`
2. Validate configuration: `haproxy -c -f /etc/haproxy/haproxy.cfg`
3. Use runtime API: `/usr/local/bin/haproxy-runtime-manager.sh stats`
