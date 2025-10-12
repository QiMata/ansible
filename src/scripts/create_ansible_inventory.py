"""CLI utility for generating INI-style Ansible inventories from PostgreSQL."""
from __future__ import annotations

import argparse
import os
import shlex
from collections import defaultdict
from dataclasses import dataclass
from ipaddress import ip_address, ip_interface
from pathlib import Path
from typing import Iterable, Mapping, Sequence

try:
    import psycopg2
except ImportError:  # pragma: no cover - exercised when psycopg2 is absent
    psycopg2 = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ContainerRecord:
    """Normalized representation of a container row returned from the database."""

    environment: str
    category: str
    system: str
    application: str
    container: str
    management_ip: str
    service_ip: str

    @classmethod
    def from_row(cls, row: Sequence[str]) -> "ContainerRecord":
        env, cat, system, container, management_ip, service_ip, application = row
        return cls(
            environment=_normalize_token(env),
            category=_normalize_token(cat),
            system=_normalize_token(system),
            application=_normalize_token(application),
            container=_normalize_token(container),
            management_ip=_sanitize_ip(management_ip),
            service_ip=_sanitize_ip(service_ip),
        )


def _normalize_token(value: str) -> str:
    """Collapse spaces/dashes and strip whitespace to create inventory-safe names."""

    return value.strip().replace(" ", "_").replace("-", "_")


def _sanitize_ip(raw: str) -> str:
    """Return the canonical host IP address from an IP or CIDR string."""

    candidate = raw.strip()
    if not candidate:
        raise ValueError("Encountered empty IP address value when building inventory")

    try:
        return str(ip_interface(candidate).ip)
    except ValueError:
        # Not a CIDR value – fall back to validating a single IP address
        return str(ip_address(candidate))


def _render_host_entry(record: ContainerRecord, ansible_user: str | None, become_pass: str | None) -> str:
    parts = [
        f"{record.container}",
        f"ansible_host={record.management_ip}",
        f"service_ip={record.service_ip}",
        "ansible_become=true",
        "ansible_become_method=sudo",
    ]

    if "MARIADB_DATABASE" in record.application.upper():
        parts.append(f"galera_cluster_bind_address={record.service_ip}")
        parts.append(f"galera_cluster_address={record.service_ip}")

    if ansible_user:
        parts.append(f"ansible_user={ansible_user}")
    if become_pass:
        parts.append(f"ansible_become_pass={shlex.quote(str(become_pass))}")

    return " ".join(parts)


def _build_inventory_graph(
    records: Iterable[ContainerRecord],
    ansible_user: str | None,
    become_pass: str | None,
) -> Mapping[str, dict[str, set[str]]]:
    envs: dict[str, set[str]] = defaultdict(set)
    categories: dict[str, set[str]] = defaultdict(set)
    systems: dict[str, set[str]] = defaultdict(set)
    app_groups: dict[str, list[str]] = defaultdict(list)

    for record in records:
        environment = record.environment
        category = record.category
        system = record.system
        application_group = f"{system}_{record.application}"

        envs[environment].add(category)
        categories[category].add(system)
        systems[system].add(application_group)
        app_groups[application_group].append(_render_host_entry(record, ansible_user, become_pass))

    if not envs:
        raise ValueError("No inventory data was returned from the database query")

    return {
        "envs": envs,
        "categories": categories,
        "systems": systems,
        "app_groups": app_groups,
    }


def _write_inventory(graph: Mapping[str, dict[str, set[str]]], output_directory: Path) -> None:
    envs = graph["envs"]
    categories = graph["categories"]
    systems = graph["systems"]
    app_groups = graph["app_groups"]

    output_directory.mkdir(parents=True, exist_ok=True)

    for environment, category_names in envs.items():
        env_path = output_directory / f"{environment}.ini"
        with env_path.open("w", encoding="utf-8") as configfile:
            configfile.write("[all:children]\n")
            for category in sorted(category_names):
                configfile.write(f"{category}\n")
            configfile.write("\n")

            system_names: set[str] = set()
            for category in sorted(category_names):
                if category not in categories:
                    continue
                system_names.update(categories[category])
                configfile.write(f"[{category}:children]\n")
                for system in sorted(categories[category]):
                    configfile.write(f"{system}\n")
                configfile.write("\n")

            application_groups: set[str] = set()
            for system in sorted(system_names):
                if system not in systems:
                    continue
                application_groups.update(systems[system])
                configfile.write(f"[{system}:children]\n")
                for app_group in sorted(systems[system]):
                    configfile.write(f"{app_group}\n")
                configfile.write("\n")

            for app_group in sorted(application_groups):
                entries = app_groups.get(app_group)
                if not entries:
                    continue
                configfile.write(f"[{app_group}]\n")
                for entry in entries:
                    configfile.write(f"{entry}\n")
                configfile.write("\n")


def generate_inventory(
    rows: Iterable[Sequence[str]],
    output_directory: Path,
    ansible_user: str | None = None,
    become_pass: str | None = None,
) -> None:
    records = [ContainerRecord.from_row(row) for row in rows]
    graph = _build_inventory_graph(records, ansible_user, become_pass)
    _write_inventory(graph, output_directory)


def fetch_inventory_rows(connection) -> Iterable[Sequence[str]]:
    query = """
        SELECT e.name as env_name,
               c.name as cat_name,
               ss.name as ss_name,
               cont.container_name as cont_name,
               cont.ip_address_management,
               cont.ip_address_services,
               cont.application_type
        FROM containers cont
        JOIN server_systems ss ON cont.server_system_id = ss.id
        JOIN categories c ON ss.category_id = c.id
        JOIN environments e ON c.environment_id = e.id;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Ansible inventories from a PostgreSQL data source.")
    parser.add_argument("--db_conn_str", required=True, help="Database connection string.")
    parser.add_argument("--output_directory", required=True, help="Directory where INI files will be written.")
    parser.add_argument(
        "--ansible-user",
        default=os.environ.get("ANSIBLE_INVENTORY_USER"),
        help="SSH user for generated inventory entries (overrides ANSIBLE_INVENTORY_USER).",
    )
    parser.add_argument(
        "--become-pass",
        default=os.environ.get("ANSIBLE_BECOME_PASS"),
        help="Privilege escalation password for generated inventory entries (overrides ANSIBLE_BECOME_PASS).",
    )

    args = parser.parse_args(argv)

    output_directory = Path(args.output_directory)

    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required to connect to PostgreSQL. Install it before running the CLI.")

    with psycopg2.connect(args.db_conn_str) as connection:  # type: ignore[union-attr]
        rows = fetch_inventory_rows(connection)

    generate_inventory(rows, output_directory, args.ansible_user, args.become_pass)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via unit tests
    raise SystemExit(main())
