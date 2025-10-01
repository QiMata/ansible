import psycopg2
import argparse
import os


def create_ansible_inventory_server_string(env, cat, ss, app, cont, management_ip, service_ip, ansible_user=None, become_pass=None):
    inventory_str = f'{cont} ansible_host={management_ip.split("/")[0]} service_ip={service_ip.split("/")[0]} '
    if 'MARIADB_DATABASE' in app:
        inventory_str += f'galera_cluster_bind_address={service_ip.split("/")[0]} galera_cluster_address={service_ip.split("/")[0]} '

    inventory_str += 'ansible_become=true ansible_become_method=sudo'

    if ansible_user:
        inventory_str += f' ansible_user={ansible_user}'
    if become_pass:
        inventory_str += f' ansible_become_pass={become_pass}'

    return inventory_str

def create_ansible_ini_file(db_conn_str, output_directory, ansible_user=None, become_pass=None):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(db_conn_str)

    cur = conn.cursor()

    # Fetch data from the database
    cur.execute("""
        SELECT e.name as env_name, c.name as cat_name, ss.name as ss_name, 
               cont.container_name as cont_name, cont.ip_address_management, 
               cont.ip_address_services, cont.application_type
        FROM containers cont
        JOIN server_systems ss ON cont.server_system_id = ss.id
        JOIN categories c ON ss.category_id = c.id
        JOIN environments e ON c.environment_id = e.id;
    """)

    data = cur.fetchall()

    # Generate ini file structure
    sss = {}
    apps = {}
    cats = {}
    envs = {}

    for row in data:
        env, cat, ss, cont, management_ip, service_ip, app = row
        # Replace spaces or "-" with "_"
        env = env.replace(" ", "_").replace("-", "_")
        cat = cat.replace(" ", "_").replace("-", "_")
        ss = ss.replace(" ", "_").replace("-", "_")
        cont = cont.replace(" ", "_").replace("-", "_")
        app = app.replace(" ", "_").replace("-", "_")

        # Define the group name for application type
        app_group_name = f"{ss}_{app}"

        # Add to ini_structure
        if ss not in sss:
            sss[ss] = set()
        if app_group_name not in apps:
            apps[app_group_name] = []
        if cat not in cats:
            cats[cat] = set()
        if env not in envs:
            envs[env] = set()

        apps[app_group_name].append(
            create_ansible_inventory_server_string(
                env,
                cat,
                ss,
                app,
                cont,
                management_ip,
                service_ip,
                ansible_user,
                become_pass,
            )
        )
        sss[ss].add(app_group_name)
        cats[cat].add(ss)
        envs[env].add(cat)

    # Write to the ini file
    for env, cat_set in envs.items():
        with open(os.path.join(output_directory, f'{env}.ini'), 'w') as configfile:
            configfile.write('[all:children]\n')
            for cat in cat_set:
                configfile.write(f'{cat}\n')
            configfile.write("\n")

            cat_ss_set = set()
            for cat, ss_set in cats.items():
                if cat in cat_set:
                    configfile.write(f'[{cat}:children]\n')
                    for ss in ss_set:
                        cat_ss_set.add(ss)
                        configfile.write(f'{ss}\n')
                    configfile.write("\n")

            cat_app_group_set = set()
            for ss, app_group_set in sss.items():
                if ss in cat_ss_set:
                    configfile.write(f'[{ss}:children]\n')
                    for app_group_name in app_group_set:
                        cat_app_group_set.add(app_group_name)
                        configfile.write(f'{app_group_name}\n')
                    configfile.write("\n")

            for app_group_name, cont_list in apps.items():
                if app_group_name in cat_app_group_set:
                    configfile.write(f'[{app_group_name}]\n')
                    for cont in cont_list:
                        configfile.write(f'{cont}\n')
                    configfile.write("\n")

    # Close the cursor and the connection
    cur.close()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Ansible ini file from PostgreSQL database.')
    parser.add_argument('--db_conn_str', required=True, help='Database connection string.')
    parser.add_argument('--output_directory', required=True, help='Output directory path.')
    parser.add_argument(
        '--ansible-user',
        default=os.environ.get('ANSIBLE_INVENTORY_USER'),
        help='SSH user for generated inventory entries (can also be set with the ANSIBLE_INVENTORY_USER environment variable).',
    )
    parser.add_argument(
        '--become-pass',
        default=os.environ.get('ANSIBLE_BECOME_PASS'),
        help='Privilege escalation password for generated inventory entries (can also be set with the ANSIBLE_BECOME_PASS environment variable).',
    )

    args = parser.parse_args()

    create_ansible_ini_file(args.db_conn_str, args.output_directory, args.ansible_user, args.become_pass)
