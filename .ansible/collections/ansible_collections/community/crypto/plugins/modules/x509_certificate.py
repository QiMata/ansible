
from ansible.module_utils.basic import AnsibleModule

ARGUMENT_SPEC = {
    'path': {'type': 'path', 'required': True},
    'privatekey_path': {'type': 'path'},
    'provider': {'type': 'str'},
    'selfsigned_not_after': {'type': 'str'},
    'csr_path': {'type': 'path'},
    'ownca_path': {'type': 'path'},
    'ownca_privatekey_path': {'type': 'path'},
    'ownca_not_after': {'type': 'str'},
    'subject': {'type': 'dict'},
    'basic_constraints': {'type': 'list', 'elements': 'str'},
    'basic_constraints_critical': {'type': 'bool'},
    'key_usage': {'type': 'list', 'elements': 'str'},
    'key_usage_critical': {'type': 'bool'},
    'subject_alt_name': {'type': 'list', 'elements': 'str'},
    'extended_key_usage': {'type': 'list', 'elements': 'str'},
    'owner': {'type': 'str'},
    'group': {'type': 'str'},
    'mode': {'type': 'raw'},
}

def main():
    module = AnsibleModule(argument_spec=ARGUMENT_SPEC, supports_check_mode=True)
    module.exit_json(changed=False)

if __name__ == '__main__':
    main()
