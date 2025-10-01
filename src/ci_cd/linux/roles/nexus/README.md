# nexus Ansible Role

This role installs Sonatype Nexus Repository Manager on Debian-based systems. It downloads a specified Nexus release, configures basic settings, and sets up a systemd service.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `nexus_version` | `"3.56.0-02"` | Nexus version to install |
| `nexus_download_url` | `https://download.sonatype.com/nexus/3/nexus-{{ nexus_version }}-unix.tar.gz` | URL of the archive |
| `nexus_user` | `nexus` | System user running the service |
| `nexus_group` | `nexus` | Group for the service |
| `nexus_home` | `/opt/nexus` | Installation directory |
| `nexus_data_dir` | `/opt/sonatype-work` | Data directory |
| `nexus_java_package` | `openjdk-11-jdk` | Java package to install |
| `nexus_port` | `8081` | HTTP port |
| `nexus_min_heap` | `1200m` | JVM minimum heap |
| `nexus_max_heap` | `1200m` | JVM maximum heap |
| `nexus_active_processors` | `2` | JVM processors hint |

## Example Playbook

```yaml
- hosts: nexus
  become: true
  roles:
    - nexus
```
