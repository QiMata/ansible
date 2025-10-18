
from ansible.module_utils.basic import AnsibleModule

ARGUMENT_SPEC = {
    'path': {'type': 'path', 'required': True},
    'privatekey_path': {'type': 'path', 'required': True},
    'subject': {'type': 'dict'},
    'subject_alt_name': {'type': 'list', 'elements': 'str'},
    'key_usage': {'type': 'list', 'elements': 'str'},
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
