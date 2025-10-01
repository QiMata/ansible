# Nexus Repository Manager Role

This role installs and configures Sonatype Nexus Repository Manager on Debian hosts. It follows the best practices outlined in the implementation guide for idempotent tasks and modular design.

## Usage

Add hosts to the `nexus` group and apply the role:

```yaml
- hosts: nexus
  become: true
  roles:
    - nexus
```

Customize variables such as `nexus_version`, `nexus_port`, and JVM options via inventory or extra vars.
