# pfSense Ansible Role

A comprehensive Ansible role for configuring pfSense firewalls. This role manages all major components of pfSense including networking, security, VPN, and system administration.

## Requirements

- Ansible 2.9 or higher
- pfSense 2.6+ (tested with 2.6, 2.7, 23.01, 23.05, 23.09)
- `pfsensible.core` collection installed
- Network access to pfSense management interface

## Installation

1. Install the required collection:
```bash
ansible-galaxy collection install pfsensible.core
```

2. Clone or include this role in your Ansible project.

## Role Variables

### Connection Settings

```yaml
pfsense_host: "{{ ansible_host }}"
pfsense_username: admin
pfsense_password: "{{ vault_pfsense_password }}"
pfsense_scheme: https
pfsense_port: 443
pfsense_timeout: 30
pfsense_validate_certs: false
```

### Component Configuration Flags

```yaml
pfsense_configure_system_settings: true
pfsense_configure_certificates: false
pfsense_configure_interfaces: true
pfsense_configure_vlans: false
pfsense_configure_gateways: true
pfsense_configure_static_routes: false
pfsense_configure_dhcp: true
pfsense_configure_dns: true
pfsense_configure_aliases: false
pfsense_configure_nat: true
pfsense_configure_firewall_rules: true
pfsense_configure_traffic_shaping: false
pfsense_configure_user_auth: false
pfsense_configure_captive_portal: false
pfsense_configure_openvpn: false
pfsense_configure_ipsec: false
pfsense_configure_packages: false
pfsense_perform_backup: false
pfsense_perform_updates: false
```

## Usage Examples

### Basic LAN/WAN Setup

```yaml
- hosts: pfsense
  vars:
    pfsense_interfaces:
      - interface: wan
        enable: true
        descr: "WAN Interface"
        type: dhcp
      - interface: lan
        enable: true
        descr: "LAN Interface"
        type: static
        ipaddr: 192.168.1.1
        subnet: 24
    
    pfsense_dhcp_servers:
      - interface: lan
        enable: true
        range_from: "192.168.1.100"
        range_to: "192.168.1.200"
        dns_servers:
          - "192.168.1.1"
    
    pfsense_firewall_rules:
      - interface: lan
        action: pass
        protocol: any
        source: lan_net
        destination: any
        descr: "Allow LAN to any"
  
  roles:
    - networking.pfsense
```

### VLAN Configuration

```yaml
- hosts: pfsense
  vars:
    pfsense_configure_vlans: true
    pfsense_vlans:
      - tag: 10
        if: igb1
        descr: "Management VLAN"
        configure_interface: true
        type: static
        ipaddr: 192.168.10.1
        subnet: 24
      - tag: 20
        if: igb1
        descr: "Guest VLAN"
        configure_interface: true
        type: static
        ipaddr: 192.168.20.1
        subnet: 24
  
  roles:
    - networking.pfsense
```

### OpenVPN Server

```yaml
- hosts: pfsense
  vars:
    pfsense_configure_openvpn: true
    pfsense_openvpn:
      servers:
        - descr: "Remote Access VPN"
          mode: "server_user"
          protocol: "udp4"
          interface: "wan"
          local_port: 1194
          caref: "{{ ca_reference }}"
          crtref: "{{ cert_reference }}"
          tunnel_network: "10.8.0.0/24"
          local_network: "192.168.1.0/24"
          dns_server_enable: true
          dns_server1: "192.168.1.1"
          gwredir: true
  
  roles:
    - networking.pfsense
```

### IPsec Site-to-Site VPN

```yaml
- hosts: pfsense
  vars:
    pfsense_configure_ipsec: true
    pfsense_ipsec:
      enable: true
      phase1:
        - descr: "Site-to-Site VPN"
          interface: "wan"
          remote_gateway: "203.0.113.1"
          pre_shared_key: "{{ vault_ipsec_psk }}"
          encryption: "aes256"
          hash: "sha256"
          dhgroup: "14"
      phase2:
        - ikeid: 1
          descr: "Site-to-Site Tunnel"
          localid_address: "192.168.1.0"
          localid_netbits: 24
          remoteid_address: "192.168.2.0"
          remoteid_netbits: 24
          encryption: "aes256"
          hash: "sha256"
  
  roles:
    - networking.pfsense
```

### Traffic Shaping/QoS

```yaml
- hosts: pfsense
  vars:
    pfsense_configure_traffic_shaping: true
    pfsense_traffic_shaping:
      enable: true
      limiters:
        - name: "UploadLimiter"
          bandwidth: 100
          bandwidthtype: "Mb"
          mask: "srcaddress"
          descr: "Upload bandwidth limiter"
        - name: "DownloadLimiter"
          bandwidth: 100
          bandwidthtype: "Mb"
          mask: "dstaddress"
          descr: "Download bandwidth limiter"
      rules:
        - interface: "lan"
          action: "pass"
          protocol: "tcp"
          source: "lan_net"
          destination: "any"
          destination_port: "80,443"
          dnpipe: "UploadLimiter"
          pdnpipe: "DownloadLimiter"
          descr: "Web traffic shaping"
  
  roles:
    - networking.pfsense
```

### Package Management

```yaml
- hosts: pfsense
  vars:
    pfsense_configure_packages: true
    pfsense_packages:
      install:
        - pfBlockerNG
        - Suricata
        - ntopng
      remove:
        - Snort
  
  roles:
    - networking.pfsense
```

## Available Tags

Run specific components using tags:

```bash
# Configure only interfaces
ansible-playbook site.yml --tags "interfaces"

# Configure firewall rules and NAT
ansible-playbook site.yml --tags "firewall,nat"

# Configure VPN components
ansible-playbook site.yml --tags "vpn"

# Perform backup
ansible-playbook site.yml --tags "backup"
```

Available tags:
- `system`, `system_settings`
- `certificates`, `ssl`
- `interfaces`, `lans`, `network`
- `vlans`
- `gateways`, `routing`
- `routes`
- `dhcp`
- `dns`, `resolver`
- `aliases`
- `nat`
- `firewall`, `rules`
- `qos`, `traffic_shaping`
- `auth`, `users`
- `captive_portal`, `guest`
- `openvpn`, `vpn`
- `ipsec`, `s2s`
- `packages`
- `backup`
- `updates`, `maintenance`

## Security Considerations

1. **Credentials**: Always use Ansible Vault for passwords and sensitive data:
   ```yaml
   pfsense_password: "{{ vault_pfsense_password }}"
   ```

2. **Certificate Validation**: Enable certificate validation in production:
   ```yaml
   pfsense_validate_certs: true
   ```

3. **Backup Encryption**: Use encrypted backups:
   ```yaml
   pfsense_backup:
     enabled: true
     encryption_password: "{{ vault_backup_password }}"
   ```

4. **Limited User Access**: Create dedicated Ansible user with minimal required privileges.

## Dependencies

- `pfsensible.core` collection

## License

MIT

## Author Information

Systems Admin Team - Your Organization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions:
- Create an issue in the project repository
- Check pfSense documentation: https://docs.netgate.com/pfsense/
- Review pfsensible.core collection documentation
