# Jenkins SSL/TLS Configuration Role

**Table of Contents**

* [Overview](#overview)
* [Supported Operating Systems/Platforms](#supported-operating-systemsplatforms)
* [Role Variables](#role-variables)
* [Dependencies](#dependencies)
* [Example Playbook](#example-playbook)
* [Security Implications](#security-implications)

## Overview

The **jenkins_ssl** role configures SSL/TLS encryption for Jenkins to enable secure HTTPS communication. This role handles certificate generation (self-signed or custom), Java keystore creation, Jenkins SSL configuration, and optional HTTP to HTTPS redirection.

Key features:
* **Certificate Management**: Automatically generates self-signed certificates or uses provided certificates
* **Java Keystore Creation**: Converts certificates to Java keystore format required by Jenkins
* **SSL Configuration**: Configures Jenkins to use HTTPS with proper security settings
* **Proxy Support**: Handles configuration for Jenkins behind SSL-terminating proxies
* **Security Headers**: Configures security headers for enhanced protection

## Supported Operating Systems/Platforms

This role is tested on and designed for **Debian** and **Ubuntu** Linux distributions:

* **Debian** – 11 (Bullseye) and 12 (Bookworm)
* **Ubuntu** – 20.04 LTS (Focal) and 22.04 LTS (Jammy)

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# SSL/TLS Configuration for Jenkins
jenkins_ssl_enabled: false
jenkins_ssl_port: 8443
jenkins_ssl_keystore_path: "{{ jenkins_controller_home | default('/var/lib/jenkins') }}/jenkins.jks"
jenkins_ssl_keystore_password: "{{ vault_jenkins_ssl_keystore_password | default('changeit') }}"
jenkins_ssl_certificate_path: "/etc/ssl/certs/jenkins.crt"
jenkins_ssl_private_key_path: "/etc/ssl/private/jenkins.key"
jenkins_ssl_redirect_http: true
jenkins_ssl_disable_http: false

# Certificate generation options
jenkins_ssl_generate_self_signed: true
jenkins_ssl_cert_subject:
  common_name: "{{ ansible_fqdn }}"
  country_name: US
  state_or_province_name: State
  locality_name: City
  organization_name: Organization
jenkins_ssl_subject_alt_names:
  - "DNS:{{ ansible_fqdn }}"
  - "DNS:{{ ansible_hostname }}"
  - "IP:{{ ansible_default_ipv4.address }}"
jenkins_ssl_cert_days: 365
```

## Dependencies

* Requires the `jenkins_controller` role to be run first
* OpenSSL must be available on the target system
* Java keytool utility (included with OpenJDK)

## Example Playbook

```yaml
---
- hosts: jenkins_controllers
  become: true
  roles:
    - jenkins_controller
    - role: jenkins_ssl
      vars:
        jenkins_ssl_enabled: true
        jenkins_ssl_port: 8443
        jenkins_ssl_disable_http: true
        vault_jenkins_ssl_keystore_password: "secure-keystore-password"
```

## Security Implications

* **Certificate Security**: Store keystore passwords in Ansible Vault
* **Self-Signed Certificates**: Only use for development/testing environments
* **Production Deployment**: Use certificates from trusted Certificate Authorities
* **Firewall Configuration**: Ensure proper firewall rules for HTTPS port
* **HTTP Redirect**: Consider disabling HTTP entirely in production environments
