import argparse
from proxmoxer import ProxmoxAPI

# Set up command line argument parsing
parser = argparse.ArgumentParser(description='Generate a BIND9 domain file using the Proxmox API.')
parser.add_argument('--host', required=True, help='Proxmox host')
parser.add_argument('--user', required=True, help='Proxmox user')
parser.add_argument('--password', required=True, help='Proxmox password')
parser.add_argument('--domain', required=True, help='Domain name')

# Parse command line arguments
args = parser.parse_args()

proxmox_host = args.host
proxmox_user = args.user
proxmox_password = args.password
domain = args.domain

# Connect to Proxmox API
proxmox = ProxmoxAPI(proxmox_host, user=proxmox_user, password=proxmox_password, verify_ssl=False)

# Get list of all nodes
nodes = proxmox.nodes.get()

bind_file_content = ""
for node in nodes:
    node_ip = node['ip']
    node_name = node['node']

    # Append node to BIND9 file content
    bind_file_content += f"{node_name} IN A {node_ip}\n"

    # Get list of all QEMU/KVM VMs
    vms_qemu = proxmox.nodes(node['node']).qemu.get()
    for vm in vms_qemu:
        ip = proxmox.nodes(node['node']).qemu(vm['vmid']).agent.network_get()['result']['lo']['ip-addresses'][0]['ip-address']
        hostname = vm['name']

        # Append VM to BIND9 file content
        bind_file_content += f"{hostname} IN A {ip}\n"

    # Get list of all LXC containers
    vms_lxc = proxmox.nodes(node['node']).lxc.get()
    for vm in vms_lxc:
        ip = proxmox.nodes(node['node']).lxc(vm['vmid']).status.current.get()['ip']
        hostname = vm['name']

        # Append VM to BIND9 file content
        bind_file_content += f"{hostname} IN A {ip}\n"

# Write to BIND9 file
with open("db." + domain, "w") as f:
    f.write(bind_file_content)

print(f"DNS file for domain {domain} was successfully created.")
