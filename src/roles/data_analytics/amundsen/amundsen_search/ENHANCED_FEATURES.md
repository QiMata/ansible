# Enhanced Amundsen Search Role

## New Features Added

This enhanced version of the Amundsen Search role includes the following advanced features:

### 🔐 Security & Authentication

- **Elasticsearch Authentication**: Support for basic auth, API keys, and X-Pack security
- **Service Authentication**: API key and JWT-based authentication for the search service
- **TLS/SSL Configuration**: Full HTTPS support with certificate management
- **Mutual TLS**: Client certificate authentication with Elasticsearch

### 🔄 High Availability & Scaling

- **Load Balancer Support**: Configuration for deployment behind HAProxy/NGINX
- **Multi-Instance Deployment**: Support for running multiple search service instances
- **Health Checks**: Built-in health monitoring and endpoint checks
- **Graceful Shutdown**: Proper signal handling and graceful service termination

### 📊 Monitoring & Observability

- **Prometheus Metrics**: Native Prometheus metrics export
- **StatsD Integration**: Support for StatsD metric collection
- **Structured Logging**: JSON and standard log format options
- **Access Logging**: Detailed request logging with rotation
- **Query Analytics**: Search query logging and slow query detection

### 🗃️ Index Management

- **Lifecycle Policies**: Automated index lifecycle management
- **Index Templates**: Custom Elasticsearch mapping templates
- **Index Warming**: Predefined query execution for cache warming
- **Data Retention**: Automated cleanup of old indices
- **Index Optimization**: Scheduled forcemerge operations

### 💾 Backup & Recovery

- **Automated Backups**: Scheduled Elasticsearch snapshot creation
- **Backup Cleanup**: Retention policy-based backup cleanup
- **Restore Scripts**: Tools for data restoration from snapshots
- **Repository Management**: Elasticsearch snapshot repository configuration

### ⚡ Performance & Caching

- **Redis Caching**: Response caching with Redis backend
- **Memory Caching**: In-memory response caching option
- **Connection Pooling**: Optimized Elasticsearch connection management
- **Query Optimization**: Fuzzy search and result size tuning

### 🎯 Environment Configuration

- **Environment-Specific Configs**: Development, staging, and production configurations
- **Custom Variables**: Support for custom configuration variables
- **Debug Mode**: Enhanced debugging capabilities for development

## Example Configurations

### Production Deployment with Full Security

```yaml
# Production configuration with all security features
amundsen_search_environment: "production"
amundsen_search_tls_enabled: true
amundsen_search_auth_enabled: true
amundsen_search_es_auth_enabled: true
amundsen_search_es_tls_enabled: true
amundsen_search_metrics_enabled: true
amundsen_search_backup_enabled: true
amundsen_search_index_management_enabled: true
```

### High Availability Cluster

```yaml
# Multi-instance deployment
amundsen_search_multi_instance: true
amundsen_search_behind_lb: true
amundsen_search_cluster_nodes:
  - "search-1.example.com:5001"
  - "search-2.example.com:5001"
  - "search-3.example.com:5001"
```

### Development Environment

```yaml
# Development with debugging enabled
amundsen_search_environment: "development"
amundsen_search_debug: true
amundsen_search_log_level: "DEBUG"
amundsen_search_auth_enabled: false
amundsen_search_tls_enabled: false
```

## Testing

The role includes comprehensive tests for all enhanced features:

- **Basic functionality tests**: Service installation and configuration
- **Security tests**: Authentication and TLS validation
- **Monitoring tests**: Health checks and metrics endpoints
- **Integration tests**: End-to-end functionality verification

Run tests with:
```bash
molecule test
```

## Integration with Existing Roles

This enhanced role automatically integrates with existing roles in the repository:

- **Elasticsearch Role**: For authentication and TLS configuration
- **HAProxy Role**: For load balancer setup
- **Prometheus Role**: For monitoring integration
- **Grafana Role**: For dashboard provisioning

## Migration Guide

To upgrade from the basic role to the enhanced version:

1. Review new default variables in `defaults/main.yml`
2. Enable desired features gradually in a staging environment
3. Update any existing playbooks to use new variable names
4. Test thoroughly before production deployment

## Support Matrix

| Feature | Ubuntu 20.04 | Ubuntu 22.04 | RHEL 8/9 | Notes |
|---------|--------------|--------------|----------|--------|
| Basic Installation | ✅ | ✅ | ✅ | Full support |
| TLS/SSL | ✅ | ✅ | ✅ | Requires certificates |
| Authentication | ✅ | ✅ | ✅ | All auth types |
| Monitoring | ✅ | ✅ | ✅ | Prometheus/StatsD |
| Multi-instance | ✅ | ✅ | ✅ | systemd dependent |
| Backup/Restore | ✅ | ✅ | ✅ | ES 7.0+ required |

## Troubleshooting

### Common Issues

1. **Service fails to start**: Check Elasticsearch connectivity and credentials
2. **Authentication issues**: Verify API keys or JWT secrets are properly configured
3. **TLS certificate errors**: Ensure certificate paths and permissions are correct
4. **Monitoring not working**: Check Prometheus port availability and firewall rules

### Debug Mode

Enable debug mode for detailed logging:
```yaml
amundsen_search_debug: true
amundsen_search_log_level: "DEBUG"
```

### Health Check Script

Use the built-in health check script:
```bash
/opt/amundsen/search/venv/bin/python /opt/amundsen/search/venv/health_check.py --full-check
```
