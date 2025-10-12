# data_systems.mariadb (stub)

This lightweight collection exposes the existing MariaDB sub-roles that live under
`src/roles/data_systems/mariadb/` so that tooling such as ansible-lint can resolve
fully qualified role names (e.g. `data_systems.mariadb.mariadb_backups`) without
needing to alter the global `roles_path` configuration.

The collection mirrors the role implementations via symbolic links and is not
intended for distribution.
