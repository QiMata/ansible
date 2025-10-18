
from ansible.module_utils.basic import AnsibleModule

ARGUMENT_SPEC = {
    'path': {'type': 'path', 'required': True},
    'size': {'type': 'int'},
    'owner': {'type': 'str'},
    'group': {'type': 'str'},
    'mode': {'type': 'raw'},
}

def main():
    module = AnsibleModule(argument_spec=ARGUMENT_SPEC, supports_check_mode=True)
    module.exit_json(changed=False)

if __name__ == '__main__':
    main()
