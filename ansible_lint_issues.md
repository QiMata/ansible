# Initial ansible-lint findings

The following list captures the first 100 ansible-lint findings detected in `src/roles/data_analytics/airflow`.

- src/roles/data_analytics/airflow/airflow_connector/defaults/main.yml:5:1: var-naming[no-role-prefix]: Variables names from within roles should use airflow_connector_ as a prefix. (vars: airflow_home)
- src/roles/data_analytics/airflow/airflow_connector/defaults/main.yml:6:1: var-naming[no-role-prefix]: Variables names from within roles should use airflow_connector_ as a prefix. (vars: airflow_binary_path)
- src/roles/data_analytics/airflow/airflow_connector/defaults/main.yml:50:1: var-naming[no-role-prefix]: Variables names from within roles should use airflow_connector_ as a prefix. (vars: airflow_connections)
- src/roles/data_analytics/airflow/airflow_connector/defaults/main.yml:53:1: var-naming[no-role-prefix]: Variables names from within roles should use airflow_connector_ as a prefix. (vars: airflow_connections_to_delete)
- src/roles/data_analytics/airflow/airflow_connector/defaults/main.yml:60:1: var-naming[no-role-prefix]: Variables names from within roles should use airflow_connector_ as a prefix. (vars: airflow_connections_export_secure)
- src/roles/data_analytics/airflow/airflow_connector/handlers/main.yml:4:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_connector/handlers/main.yml:9: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/handlers/main.yml:13:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_connector/handlers/main.yml:18: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/handlers/main.yml:22:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_connector/handlers/main.yml:27: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/meta/main.yml:1: schema[meta][/]: $.galaxy_info.platforms[0].versions[0] 18.04 is not one of ['6.1', '7.1', '7.2', 'all']. See https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#using-role-dependencies[/]
- src/roles/data_analytics/airflow/airflow_connector/meta/main.yml:10: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/molecule/default/converge.yml:64:9: var-naming[no-role-prefix]: Variables names from within roles should use airflow_connector_ as a prefix. (vars: airflow_connections)
- src/roles/data_analytics/airflow/airflow_connector/molecule/default/converge.yml:73: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/molecule/default/converge.yml:78: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/molecule/proxmox/molecule.yml:32: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/airflow_connector/molecule/proxmox/molecule.yml:39: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/airflow_connector/molecule/proxmox/molecule.yml:40: yaml[line-length]: Line too long (441 > 160 characters)
- src/roles/data_analytics/airflow/airflow_connector/molecule/proxmox/molecule.yml:58: yaml[empty-lines]: Too many blank lines (1 > 0)
- src/roles/data_analytics/airflow/airflow_connector/molecule/proxmox/prepare.yml:12: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/tasks/create_connections.yml:20: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/tasks/create_connections.yml:27: no-changed-when: Commands should not change things if nothing needs doing.
- src/roles/data_analytics/airflow/airflow_connector/tasks/create_connections.yml:42: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/tasks/create_connections.yml:43: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/tasks/create_connections.yml:61: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_connector/tasks/delete_connections.yml:19: yaml[line-length]: Line too long (213 > 160 characters)
- src/roles/data_analytics/airflow/airflow_connector/tasks/export_connections.yml:30: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/airflow_scheduler/handlers/main.yml:2:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_scheduler/handlers/main.yml:6:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_scheduler/meta/main.yml:1: schema[meta][/]: $.galaxy_info.platforms[0].versions[0] 18.04 is not one of ['6.1', '7.1', '7.2', 'all']. See https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#using-role-dependencies[/]
- src/roles/data_analytics/airflow/airflow_webserver/handlers/main.yml:2:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_webserver/handlers/main.yml:6:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/airflow_webserver/meta/main.yml:1: schema[meta][/]: $.galaxy_info.platforms[0].versions[0] 18.04 is not one of ['6.1', '7.1', '7.2', 'all']. See https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html#using-role-dependencies[/]
- src/roles/data_analytics/airflow/apache_airflow/defaults/main.yml:38: yaml[line-length]: Line too long (246 > 160 characters)
- src/roles/data_analytics/airflow/apache_airflow/defaults/main.yml:51: yaml[line-length]: Line too long (163 > 160 characters)
- src/roles/data_analytics/airflow/apache_airflow/handlers/main.yml:2:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/apache_airflow/handlers/main.yml:24:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/apache_airflow/handlers/main.yml:30:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/apache_airflow/handlers/main.yml:36:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/apache_airflow/handlers/main.yml:42:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/apache_airflow/handlers/main.yml:48:9: name[casing][/]: All names should start with an uppercase letter.
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:26: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:27: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:32: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:33: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:34: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:39: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:42: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:43: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:52: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:58: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:59: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:66: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:68:22: schema[playbook][/]: 'become_method' must be one of the currently available values: ansible.builtin.runas, ansible.builtin.su, ansible.builtin.sudo, ansible.netcommon.enable, community.general.doas, community.general.dzdo, community.general.ksu, community.general.machinectl, community.general.pbrun, community.general.pfexec, community.general.pmrun, community.general.run0, community.general.sesu, community.general.sudosu, containers.podman.podman_unshare
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:73: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:77: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:79:22: schema[playbook][/]: 'become_method' must be one of the currently available values: ansible.builtin.runas, ansible.builtin.su, ansible.builtin.sudo, ansible.netcommon.enable, community.general.doas, community.general.dzdo, community.general.ksu, community.general.machinectl, community.general.pbrun, community.general.pfexec, community.general.pmrun, community.general.run0, community.general.sesu, community.general.sudosu, containers.podman.podman_unshare
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:81: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:82: command-instead-of-shell: Use shell only when shell functionality is required.
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:86: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:88:22: schema[playbook][/]: 'become_method' must be one of the currently available values: ansible.builtin.runas, ansible.builtin.su, ansible.builtin.sudo, ansible.netcommon.enable, community.general.doas, community.general.dzdo, community.general.ksu, community.general.machinectl, community.general.pbrun, community.general.pfexec, community.general.pmrun, community.general.run0, community.general.sesu, community.general.sudosu, containers.podman.podman_unshare
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/converge.yml:99: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/molecule.yml:32: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/molecule.yml:39: yaml[truthy][/]: Truthy value should be one of [false, true]
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/molecule.yml:40: yaml[line-length]: Line too long (441 > 160 characters)
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/molecule.yml:58: yaml[empty-lines]: Too many blank lines (1 > 0)
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:7: run-once[task][/]: Using run_once may behave differently if strategy is set to free.
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:8:7: fqcn[action-core]: Use FQCN for builtin module actions (debug).
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:17: run-once[task][/]: Using run_once may behave differently if strategy is set to free.
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:18:7: fqcn[action-core]: Use FQCN for builtin module actions (wait_for).
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:28:7: fqcn[action-core]: Use FQCN for builtin module actions (ping).
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:32:7: fqcn[action-core]: Use FQCN for builtin module actions (setup).
- src/roles/data_analytics/airflow/apache_airflow/molecule/proxmox/prepare.yml:39: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:11:3: fqcn[action][/]: Use FQCN for module actions, such `community.postgresql.postgresql_user`.
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:18: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:24:3: fqcn[action][/]: Use FQCN for module actions, such `community.postgresql.postgresql_db`.
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:30: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:36:3: fqcn[action][/]: Use FQCN for module actions, such `community.mysql.mysql_user`.
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:42: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:48:3: fqcn[action][/]: Use FQCN for module actions, such `community.mysql.mysql_db`.
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:51: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/database.yml:57:3: fqcn[action-core]: Use FQCN for builtin module actions (wait_for).
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:15: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:25: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:34: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:44: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:64: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:72:3: fqcn[action-core]: Use FQCN for builtin module actions (wait_for).
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:76: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:81:3: fqcn[action-core]: Use FQCN for builtin module actions (wait_for).
- src/roles/data_analytics/airflow/apache_airflow/tasks/executor.yml:85: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/rbac.yml:64: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/rbac.yml:65: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/scheduler_ha.yml:37: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/scheduler_ha.yml:64: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/ssl.yml:12: key-order[task][/]: You can improve the task key order to: name, when, block
- src/roles/data_analytics/airflow/apache_airflow/tasks/ssl.yml:34: yaml[trailing-spaces]: Trailing spaces
- src/roles/data_analytics/airflow/apache_airflow/tasks/ssl.yml:38: key-order[task][/]: You can improve the task key order to: name, when, block
- src/roles/data_analytics/airflow/apache_airflow/tasks/ssl.yml:44:9: var-naming[no-role-prefix]: Variables names from within roles should use letsencrypt_setup_ as a prefix. (vars: letsencrypt_domains)

## Remediation priorities

- **Variable naming** (`var-naming[no-role-prefix]`): rename role variables to include the correct `airflow_connector_` or `letsencrypt_setup_` prefixes while keeping backwards compatibility by introducing aliased defaults.
- **Handler naming conventions** (`name[casing]`): update handler names so they start with uppercase letters.
- **YAML formatting** (`yaml[trailing-spaces]`, `yaml[line-length]`, `yaml[empty-lines]`, `yaml[truthy]`): remove trailing spaces, wrap long lines, normalize boolean values to `true`/`false`, and collapse redundant blank lines.
- **Metadata compliance** (`schema[meta]`, `schema[playbook]`): adjust role metadata values (e.g., supported platform versions, `become_method`) to match ansible-lint expectations.
- **Module usage** (`fqcn`, `command-instead-of-shell`, `no-changed-when`, `run-once`, `key-order`): replace bare module names with their fully qualified collection names, ensure shell usage is justified or switched to command modules, annotate commands with `changed_when`, remove unnecessary `run_once`, and order task keys consistently.

## Resolution summary

- Updated role defaults to use prefixed variables and added compatibility fallbacks for legacy variable names.
- Normalized handler naming, metadata platform declarations, and Molecule settings to comply with ansible-lint schemas.
- Eliminated formatting violations (trailing spaces, excessive line length, blank lines, truthy values) across connector and apache_airflow roles.
- Replaced bare module names with fully qualified collection names and added explicit `changed_when`/`failed_when` guards for command tasks.
- Ensured shell usage is minimized by relying on `ansible.builtin.command` with environment overrides.

## Validation

- `ansible-lint src/roles/data_analytics/airflow/airflow_connector -p`
- `ansible-lint src/roles/data_analytics/airflow/apache_airflow -p`
- `ansible-lint src/roles/data_analytics/airflow/airflow_scheduler -p`
- `ansible-lint src/roles/data_analytics/airflow/airflow_webserver -p`
