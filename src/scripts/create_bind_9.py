import argparse
import sys
from ipaddress import ip_address
from proxmoxer import ProxmoxAPI

"""Generate a BIND9 zone file populated from a Proxmox cluster.

The script queries nodes, QEMU virtual machines, and LXC containers to build
`A`/`AAAA` records for the provided domain. QEMU virtual machines require the
guest agent with the `network-get` command enabled; machines without a
non-loopback address reported by the agent are skipped with a warning. LXC
containers are inspected through the status endpoint and likewise skipped when
no usable IP address is advertised. Running the script therefore requires API
credentials with sufficient privileges to call those endpoints.
"""

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


def _format_bind_record(hostname, address):
    """Return a BIND record line for the provided hostname and IP address."""

    record_type = "AAAA" if address.version == 6 else "A"
    return f"{hostname} IN {record_type} {address}"


def _first_non_loopback_guest_ip(agent_network):
    """Return the first non-loopback IP address reported by the guest agent."""

    if not isinstance(agent_network, dict):
        return None

    result = agent_network.get('result', {})
    if not isinstance(result, dict):
        return None

    for interface, data in result.items():
        if not isinstance(data, dict):
            continue

        addresses = data.get('ip-addresses', [])
        if not isinstance(addresses, list):
            continue

        for address in addresses:
            if not isinstance(address, dict):
                continue

            ip_value = address.get('ip-address')
            if not ip_value:
                continue

            try:
                parsed = ip_address(ip_value)
            except ValueError:
                continue

            if parsed.is_loopback:
                continue

            return parsed

    return None


def _first_non_loopback_lxc_ip(status):
    """Return the first non-loopback IP address reported for an LXC container."""

    if not isinstance(status, dict):
        return None

    candidates = []

    def _extend_from_field(field):
        if isinstance(field, str):
            candidates.extend(part.strip() for part in field.split() if part.strip())
        elif isinstance(field, dict):
            ip_value = field.get('ip') or field.get('address')
            if ip_value:
                candidates.append(ip_value)
        elif isinstance(field, list):
            for item in field:
                _extend_from_field(item)

    _extend_from_field(status.get('ip'))
    _extend_from_field(status.get('ip6'))

    for candidate in candidates:
        ip_value = candidate.split('/', 1)[0]
        try:
            parsed = ip_address(ip_value)
        except ValueError:
            continue

        if parsed.is_loopback:
            continue

        return parsed

    return None


for node in nodes:
    node_ip = node['ip']
    node_name = node['node']

    try:
        node_address = ip_address(node_ip)
    except ValueError:
        print(
            f"Warning: skipping node '{node_name}' - invalid IP address '{node_ip}'",
            file=sys.stderr,
        )
        node_address = None

    if node_address:
        # Append node to BIND9 file content
        bind_file_content += _format_bind_record(node_name, node_address) + "\n"

    # Get list of all QEMU/KVM VMs
    vms_qemu = proxmox.nodes(node['node']).qemu.get()
    for vm in vms_qemu:
        hostname = vm['name']
        try:
            agent_network = proxmox.nodes(node['node']).qemu(vm['vmid']).agent.network_get()
        except Exception as exc:  # noqa: BLE001 - proxmoxer may raise varied exceptions
            print(
                f"Warning: skipping VM '{hostname}' (vmid {vm['vmid']}) on node '{node_name}' - guest agent query failed: {exc}",
                file=sys.stderr,
            )
            continue

        ip_address_obj = _first_non_loopback_guest_ip(agent_network)
        if not ip_address_obj:
            print(
                f"Warning: skipping VM '{hostname}' (vmid {vm['vmid']}) on node '{node_name}' - no non-loopback IP reported by guest agent",
                file=sys.stderr,
            )
            continue

        # Append VM to BIND9 file content
        bind_file_content += _format_bind_record(hostname, ip_address_obj) + "\n"

    # Get list of all LXC containers
    vms_lxc = proxmox.nodes(node['node']).lxc.get()
    for vm in vms_lxc:
        hostname = vm['name']
        status = proxmox.nodes(node['node']).lxc(vm['vmid']).status.current.get()
        ip_address_obj = _first_non_loopback_lxc_ip(status)
        if not ip_address_obj:
            print(
                f"Warning: skipping LXC '{hostname}' (vmid {vm['vmid']}) on node '{node_name}' - unable to determine non-loopback IP",
                file=sys.stderr,
            )
            continue

        # Append VM to BIND9 file content
        bind_file_content += _format_bind_record(hostname, ip_address_obj) + "\n"

# Write to BIND9 file
with open("db." + domain, "w") as f:
    f.write(bind_file_content)

print(f"DNS file for domain {domain} was successfully created.")
