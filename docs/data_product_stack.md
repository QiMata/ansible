# Data Product Stack Playbook

The `src/playbooks/data_product.yml` playbook orchestrates a full data platform made up of
foundational infrastructure, storage, orchestration, analytics, and observability services.
It is designed so that operators can adjust individual building blocks while maintaining
clear dependencies across the stack.

## Inventory layout

Example hosts for each layer live in `inventories/data_product.ini`. The inventory defines
dedicated groups for PostgreSQL, RabbitMQ, Apache Airflow (scheduler/webserver/worker),
Apache Spark (master/workers), Apache NiFi, MinIO, the Amundsen suite, Apache Superset,
Prometheus, Grafana, and an optional Elasticsearch endpoint consumed by dashboards. The
`[airflow:children]` group collects the scheduler, webserver, and worker groups so the
shared Airflow defaults from `src/group_vars/airflow*.yml` apply consistently.

## Service dependencies

* **PostgreSQL** (`postgresql` group) provisions the metadata databases for both Airflow
  and Superset. Database definitions, users, and HBA rules are declared in
  `src/group_vars/all/data_product.yml` and `src/group_vars/postgresql.yml`.
* **RabbitMQ** (`rabbitmq` group) acts as the Celery broker for Airflow. The broker URL
  and credentials are referenced by the Airflow and Superset groups.
* **Airflow** scheduler, webserver, and worker hosts all receive Celery configuration,
  share the Postgres metadata database, and reuse the message broker details.
  The scheduler play triggers `airflow db upgrade` after the role finishes so migrations
  run whenever a new database or Airflow version is deployed.
* **Superset** relies on the same PostgreSQL host, using a dedicated database and user.
  The Superset Celery broker can reuse the Airflow RabbitMQ instance for consistency.
* **Amundsen** exposes metadata and search APIs that the frontend consumes. The metadata
  service points at an external Neo4j instance (defined in `group_vars/amundsen_metadata.yml`)
  while the search service targets Elasticsearch.
* **MinIO** provides object storage secured with TLS; generated certificates feed both the
  S3 API and console.
* **Prometheus** scrapes exporters running on Airflow, Spark, NiFi, and MinIO hosts using
  the scrape configuration defined in `src/group_vars/prometheus.yml`.
* **Grafana** ships with a Prometheus datasource pointing to the Prometheus group and an
  Elasticsearch datasource for log analytics. Datasource URLs can be customized in
  `src/group_vars/grafana.yml`.

## Secrets and vault integration

All sensitive values referenced by the stack use vault placeholders, such as
`vault_airflow_db_password`, `vault_superset_secret_key`, and `vault_grafana_admin_password`.
Populate these variables in your vaulted `group_vars/all/vault.yml` file or in a dedicated
vault file loaded via `ansible-vault`. The sample values in the group variable files
highlight where credentials are required without exposing defaults.

## Running the composite playbook

1. Populate or override the inventory at `inventories/data_product.ini` with your hosts.
2. Provide the required vault variables listed in the group variables files.
3. Run the composite playbook: `ansible-playbook -i inventories/data_product.ini src/playbooks/data_product.yml`.

The playbook sequences base OS preparation, database provisioning, messaging, orchestration,
data services, and monitoring so dependencies (metadata migrations, brokers, and metrics)
are ready before dependent services start.

## Smoke testing

A Molecule scenario (`molecule/data_product`) is provided to run a syntax check and ensure
the playbook and inventory remain well-formed. It can be executed locally with
`molecule test -s data_product`.
