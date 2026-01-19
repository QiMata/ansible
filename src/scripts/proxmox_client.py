from __future__ import annotations

import logging
from dataclasses import dataclass
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Iterable

from proxmoxer import ProxmoxAPI

IPAddress = IPv4Address | IPv6Address


@dataclass(frozen=True)
class ProxmoxAuth:
    host: str
    user: str
    password: str
    verify_ssl: bool = False


def connect(auth: ProxmoxAuth):
    return ProxmoxAPI(auth.host, user=auth.user, password=auth.password, verify_ssl=auth.verify_ssl)


def first_non_loopback_guest_ip(agent_network: dict) -> IPAddress | None:
    if not isinstance(agent_network, dict):
        return None

    result = agent_network.get("result", {})
    if not isinstance(result, dict):
        return None

    for data in result.values():
        if not isinstance(data, dict):
            continue

        addresses = data.get("ip-addresses", [])
        if not isinstance(addresses, list):
            continue

        for address in addresses:
            if not isinstance(address, dict):
                continue

            ip_value = address.get("ip-address")
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


def first_non_loopback_lxc_ip(status: dict) -> IPAddress | None:
    if not isinstance(status, dict):
        return None

    candidates: list[str] = []

    def extend_from_field(field):
        if isinstance(field, str):
            candidates.extend(part.strip() for part in field.split() if part.strip())
        elif isinstance(field, dict):
            ip_value = field.get("ip") or field.get("address")
            if ip_value:
                candidates.append(ip_value)
        elif isinstance(field, list):
            for item in field:
                extend_from_field(item)

    extend_from_field(status.get("ip"))
    extend_from_field(status.get("ip6"))

    for candidate in candidates:
        ip_value = candidate.split("/", 1)[0]
        try:
            parsed = ip_address(ip_value)
        except ValueError:
            continue

        if parsed.is_loopback:
            continue

        return parsed

    return None


def collect_dns_records(proxmox, logger: logging.Logger) -> Iterable[tuple[str, IPAddress]]:
    for node in proxmox.nodes.get():
        node_ip = node.get("ip")
        node_name = node.get("node")

        try:
            node_address = ip_address(node_ip)
        except ValueError:
            logger.warning("Skipping node '%s' - invalid IP address '%s'", node_name, node_ip)
            node_address = None

        if node_address:
            yield node_name, node_address

        vms_qemu = proxmox.nodes(node_name).qemu.get()
        for vm in vms_qemu:
            hostname = vm.get("name")
            try:
                agent_network = proxmox.nodes(node_name).qemu(vm["vmid"]).agent.network_get()
            except Exception as exc:  # noqa: BLE001 - proxmoxer may raise varied exceptions
                logger.warning(
                    "Skipping VM '%s' (vmid %s) on node '%s' - guest agent query failed: %s",
                    hostname,
                    vm.get("vmid"),
                    node_name,
                    exc,
                )
                continue

            ip_address_obj = first_non_loopback_guest_ip(agent_network)
            if not ip_address_obj:
                logger.warning(
                    "Skipping VM '%s' (vmid %s) on node '%s' - no non-loopback IP reported by guest agent",
                    hostname,
                    vm.get("vmid"),
                    node_name,
                )
                continue

            yield hostname, ip_address_obj

        vms_lxc = proxmox.nodes(node_name).lxc.get()
        for vm in vms_lxc:
            hostname = vm.get("name")
            status = proxmox.nodes(node_name).lxc(vm["vmid"]).status.current.get()
            ip_address_obj = first_non_loopback_lxc_ip(status)
            if not ip_address_obj:
                logger.warning(
                    "Skipping LXC '%s' (vmid %s) on node '%s' - unable to determine non-loopback IP",
                    hostname,
                    vm.get("vmid"),
                    node_name,
                )
                continue

            yield hostname, ip_address_obj
