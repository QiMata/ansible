# infrastructure.truenas_vm

Creates a TrueNAS SCALE virtual machine via the v2 API using an API key. The role is idempotent by name (it skips creation if a VM with the same name already exists).

## Variables
- truenas_vm_api_url: '' — base URL to the TrueNAS API (e.g. https://truenas.example)
- truenas_vm_api_key: '' — API key for TrueNAS
- truenas_vm_validate_certs: true — validate TLS certs
- truenas_vm_validate_only: false — when true, only validates inputs (no API calls)
- truenas_vm_name: '' — VM name (required)
- truenas_vm_description: ''
- truenas_vm_time: 'UTC'
- truenas_vm_autostart: false
- truenas_vm_bootloader: 'UEFI'
- truenas_vm_cpu_mode: 'HOST-PASSTHROUGH'
- truenas_vm_vcpus: 1
- truenas_vm_cores: 1
- truenas_vm_threads: 1
- truenas_vm_memory_mib: 1024
- truenas_vm_disk_bus: 'VIRTIO'
- truenas_vm_nic_type: 'VIRTIO'
- truenas_vm_os_disk: { pool: 'apps', size: '20G', zvol_name: '' }
- truenas_vm_data_disks: [] — list of additional disks (pool defaults to data)
- truenas_vm_networks: [] — list of NICs with bridge, mac, mtu
- truenas_vm_iso_path: '' — ISO path already present on TrueNAS
- truenas_vm_cloud_init: {} — user_data/meta_data/network_config strings
- truenas_vm_additional_devices: [] — list of extra device payloads
- truenas_vm_start_on_create: true
- truenas_vm_wait_for_running: true
- truenas_vm_wait_retries: 30
- truenas_vm_wait_delay: 10

## Example (group_vars)
```yaml
# group_vars/truenas_vms.yml
truenas_vm_api_url: "https://truenas.example"
truenas_vm_api_key: "{{ vault_truenas_api_key }}"
truenas_vm_name: "web-01"
truenas_vm_description: "Web server"
truenas_vm_memory_mib: 4096
truenas_vm_vcpus: 2
truenas_vm_os_disk:
  pool: "apps"
  size: "40G"
truenas_vm_data_disks:
  - pool: "data"
    size: "200G"
truenas_vm_networks:
  - bridge: "br0"
truenas_vm_cloud_init:
  user_data: |
    #cloud-config
    users:
      - name: ubuntu
        sudo: ALL=(ALL) NOPASSWD:ALL
  network_config: |
    version: 2
    ethernets:
      eth0:
        addresses: ["192.168.1.50/24"]
        gateway4: "192.168.1.1"
        nameservers:
          addresses: ["1.1.1.1"]
```

## Example playbook
```yaml
- hosts: truenas_api
  gather_facts: false
  roles:
    - role: infrastructure.truenas_vm
```
