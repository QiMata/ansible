from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def test_nifi_single_playbook_uses_canonical_vars():
    playbook = load_yaml(REPO_ROOT / 'src/playbooks/nifi-single.yml')
    assert isinstance(playbook, list)
    play = playbook[0]
    vars_section = play.get('vars', {})
    assert 'apache_nifi_cluster_enabled' in vars_section
    assert 'apache_nifi_enable_https' in vars_section
    assert 'apache_nifi_admin_identity' in vars_section
    assert 'apache_nifi_cluster_enable' not in vars_section
    assert 'apache_nifi_security_mode' not in vars_section


def test_prometheus_monitoring_tasks_conditionally_included():
    tasks = load_yaml(REPO_ROOT / 'src/data_platform/linux/roles/apache_nifi/tasks/main.yml')
    monitoring_task = next(
        (task for task in tasks if task.get('ansible.builtin.import_tasks') == 'monitoring.yml'),
        None,
    )
    assert monitoring_task is not None
    assert monitoring_task.get('when') == 'apache_nifi_prometheus_integration'


def test_prometheus_javaagent_template_uses_canonical_variables():
    template = (REPO_ROOT / 'src/data_platform/linux/roles/apache_nifi/templates/bootstrap.conf.j2').read_text()
    assert 'apache_nifi_prometheus_integration' in template
    assert 'apache_nifi_prometheus_jmx_port' in template
    assert 'apache_nifi_prometheus_jmx_config_path' in template


def test_prometheus_monitoring_tasks_render_expected_resources():
    monitoring_tasks = load_yaml(REPO_ROOT / 'src/data_platform/linux/roles/apache_nifi/tasks/monitoring.yml')
    get_url_task = next((task for task in monitoring_tasks if task.get('ansible.builtin.get_url')), None)
    template_task = next((task for task in monitoring_tasks if task.get('ansible.builtin.template')), None)
    assert get_url_task is not None
    assert template_task is not None
    url = get_url_task['ansible.builtin.get_url']['url']
    assert '{{ apache_nifi_prometheus_jmx_exporter_version }}' in url
    dest = template_task['ansible.builtin.template']['dest']
    assert dest == '{{ apache_nifi_prometheus_jmx_config_path }}'


def test_filebeat_template_uses_logstash_hosts_variable():
    template = (REPO_ROOT / 'src/data_platform/linux/roles/apache_nifi/templates/filebeat-nifi.yml.j2').read_text()
    assert 'apache_nifi_filebeat_logstash_hosts' in template


def test_requirements_include_elastic_filebeat():
    root_reqs = load_yaml(REPO_ROOT / 'requirements.yml')
    assert any(role.get('name') == 'elastic.filebeat' for role in root_reqs.get('roles', []))
    # Ensure legacy src/requirements.yml has been retired
    assert not (REPO_ROOT / 'src/requirements.yml').exists()


def test_role_defaults_include_new_variables():
    defaults = load_yaml(REPO_ROOT / 'src/data_platform/linux/roles/apache_nifi/defaults/main.yml')
    for key in (
        'apache_nifi_prometheus_jmx_exporter_version',
        'apache_nifi_prometheus_jmx_port',
        'apache_nifi_prometheus_jmx_config_path',
        'apache_nifi_filebeat_logstash_hosts',
    ):
        assert key in defaults
