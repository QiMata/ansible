#!/usr/bin/env python3
from ansible.module_utils.basic import AnsibleModule

MODULE_PATH = "pfsensible.core.plugins.modules.pfsense_suricata_interface"


def main():
    try:
        module = __import__(MODULE_PATH, fromlist=['main'])
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith('ansible_collections.pfsensible'):
            helper = AnsibleModule(argument_spec={}, supports_check_mode=True, check_invalid_arguments=False)
            helper.fail_json(msg=(
                f"The '{MODULE_PATH}' module requires the pfsensible.core collection. "
                'Install it to enable pfSense automation.'
            ))
        raise
    else:
        module.main()


if __name__ == '__main__':
    main()
