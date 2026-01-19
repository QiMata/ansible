from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from scripts.create_ansible_inventory import fetch_inventory_rows, generate_inventory
from scripts.logging_utils import setup_logging
from scripts.proxmox_client import ProxmoxAuth, collect_dns_records, connect


def _add_log_level(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--log-level",
        default=os.environ.get("ANSIBLE_SCRIPTS_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO).",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified inventory tooling CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    db_parser = subparsers.add_parser("db-generate", help="Generate inventories from PostgreSQL.")
    db_parser.add_argument("--db-conn-str", required=True, help="Database connection string.")
    db_parser.add_argument("--output-directory", required=True, help="Directory for INI inventories.")
    db_parser.add_argument(
        "--ansible-user",
        default=os.environ.get("ANSIBLE_INVENTORY_USER"),
        help="SSH user for generated inventory entries.",
    )
    db_parser.add_argument(
        "--become-pass",
        default=os.environ.get("ANSIBLE_BECOME_PASS"),
        help="Privilege escalation password for generated inventory entries.",
    )
    _add_log_level(db_parser)

    proxmox_parser = subparsers.add_parser("proxmox-test", help="Validate Proxmox access and summarize nodes/VMs.")
    proxmox_parser.add_argument("--host", required=True, help="Proxmox host")
    proxmox_parser.add_argument("--user", required=True, help="Proxmox user")
    proxmox_parser.add_argument("--password", required=True, help="Proxmox password")
    proxmox_parser.add_argument("--verify-ssl", action="store_true", help="Enable SSL verification")
    _add_log_level(proxmox_parser)

    return parser


def _run_db_generate(args: argparse.Namespace) -> int:
    logger = setup_logging(args.log_level)
    try:
        import psycopg2  # pylint: disable=import-outside-toplevel
    except ImportError as exc:  # pragma: no cover - exercised when psycopg2 is absent
        logger.error("psycopg2 is required to connect to PostgreSQL: %s", exc)
        return 1

    output_directory = Path(args.output_directory)

    with psycopg2.connect(args.db_conn_str) as connection:
        rows = fetch_inventory_rows(connection)

    generate_inventory(rows, output_directory, args.ansible_user, args.become_pass)
    logger.info("Inventory files generated in %s", output_directory)
    return 0


def _run_proxmox_test(args: argparse.Namespace) -> int:
    logger = setup_logging(args.log_level)
    auth = ProxmoxAuth(
        host=args.host,
        user=args.user,
        password=args.password,
        verify_ssl=args.verify_ssl,
    )
    proxmox = connect(auth)
    records = list(collect_dns_records(proxmox, logger))
    logger.info("Discovered %s DNS records from Proxmox.", len(records))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "db-generate":
        return _run_db_generate(args)
    if args.command == "proxmox-test":
        return _run_proxmox_test(args)

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
