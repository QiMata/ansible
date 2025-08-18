# Jenkins Configuration as Code (CasC) Role

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Configuration Examples](#configuration-examples)

## Overview

The **jenkins_casc** role implements Jenkins Configuration as Code (CasC) to manage Jenkins configuration through YAML files. This enables version-controlled, reproducible Jenkins configurations and eliminates manual configuration drift.

Key features:
* **YAML Configuration**: Manage Jenkins settings through declarative YAML files
* **Version Control**: Track configuration changes in source control
* **Automated Deployment**: Apply configuration changes automatically
* **Configuration Validation**: Validate configuration before applying
* **Multiple Config Files**: Support for modular configuration organization

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian** and **Ubuntu** Linux distributions:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal) and 22.04 LTS (Jammy)

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Jenkins Configuration as Code settings
jenkins_casc_enabled: true
jenkins_casc_config_path: "{{ jenkins_controller_home | default('/var/lib/jenkins') }}/casc_configs"
jenkins_casc_config_file: "{{ jenkins_casc_config_path }}/jenkins.yaml"
jenkins_casc_reload_token: "{{ vault_jenkins_casc_reload_token | default('reload-config-token') }}"

# Default CasC configuration
jenkins_casc_config:
  jenkins:
    systemMessage: "Jenkins configured automatically by Ansible"
    numExecutors: 2
    mode: NORMAL
    labelString: "controller master"
    quietPeriod: 5
    scmCheckoutRetryCount: 0
```

## Dependencies

* Requires the `jenkins_controller` role to be run first
* Jenkins Configuration as Code plugin must be installed
* Appropriate Jenkins permissions for configuration management

## Example Playbook

```yaml
---
- hosts: jenkins_controllers
  become: true
  roles:
    - jenkins_controller
    - role: jenkins_casc
      vars:
        jenkins_casc_enabled: true
        jenkins_casc_config:
          jenkins:
            systemMessage: "Production Jenkins Server"
            numExecutors: 4
            securityRealm:
              local:
                allowsSignup: false
                users:
                  - id: "admin"
                    password: "{{ vault_jenkins_admin_password }}"
          security:
            globalJobDslSecurityConfiguration:
              useScriptSecurity: true
```

## Configuration Examples

### Security Configuration

```yaml
jenkins_casc_config:
  security:
    realm:
      ldap:
        configurations:
          - server: "ldap://ldap.example.com"
            rootDN: "dc=example,dc=com"
            userSearchBase: "ou=users"
    authorizationStrategy:
      globalMatrix:
        permissions:
          - "Overall/Administer:admin"
          - "Overall/Read:authenticated"
```

### Plugin Configuration

```yaml
jenkins_casc_config:
  tool:
    git:
      installations:
        - name: "Default"
          home: "/usr/bin/git"
    maven:
      installations:
        - name: "Maven 3.8"
          home: "/usr/share/maven"
```
