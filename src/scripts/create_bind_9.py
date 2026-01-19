from __future__ import annotations

import argparse
import os
from typing import Sequence

from scripts.logging_utils import setup_logging
from scripts.proxmox_client import ProxmoxAuth, collect_dns_records, connect

"""Generate a BIND9 zone file populated from a Proxmox cluster.

The script queries nodes, QEMU virtual machines, and LXC containers to build
`A`/`AAAA` records for the provided domain. QEMU virtual machines require the
guest agent with the `network-get` command enabled; machines without a
non-loopback address reported by the agent are skipped with a warning. LXC
containers are inspected through the status endpoint and likewise skipped when
no usable IP address is advertised. Running the script therefore requires API
credentials with sufficient privileges to call those endpoints.
"""


def _format_bind_record(hostname, address):
    record_type = "AAAA" if address.version == 6 else "A"
    return f"{hostname} IN {record_type} {address}"


def build_bind_records(proxmox, logger) -> str:
    lines = []
    for hostname, address in collect_dns_records(proxmox, logger):
        lines.append(_format_bind_record(hostname, address))
    return "\n".join(lines) + ("\n" if lines else "")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a BIND9 domain file using the Proxmox API.")
    parser.add_argument("--host", required=True, help="Proxmox host")
    parser.add_argument("--user", required=True, help="Proxmox user")
    parser.add_argument("--password", required=True, help="Proxmox password")
    parser.add_argument("--domain", required=True, help="Domain name")
    parser.add_argument(
        "--log-level",
        default=os.environ.get("ANSIBLE_SCRIPTS_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO).",
    )
    args = parser.parse_args(argv)

    logger = setup_logging(args.log_level)
    auth = ProxmoxAuth(host=args.host, user=args.user, password=args.password)
    proxmox = connect(auth)

    bind_file_content = build_bind_records(proxmox, logger)

    output_path = f"db.{args.domain}"
    with open(output_path, "w", encoding="utf-8") as bind_file:
        bind_file.write(bind_file_content)

    logger.info("DNS file for domain %s was successfully created at %s.", args.domain, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
