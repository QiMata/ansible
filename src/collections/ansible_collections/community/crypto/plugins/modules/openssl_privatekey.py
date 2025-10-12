#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Minimal stub of community.crypto.openssl_privatekey for ansible-lint offline usage.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: openssl_privatekey
short_description: Stub module for ansible-lint argument validation
version_added: "0.0.1"
description:
  - Provides a minimal interface compatible with community.crypto.openssl_privatekey.
options:
  path:
    description:
      - Destination path for the generated private key file.
    type: path
    required: true
  size:
    description:
      - Size of the key to generate.
    type: int
  owner:
    description:
      - File owner to set on the generated key.
    type: str
  group:
    description:
      - File group to set on the generated key.
    type: str
  mode:
    description:
      - File mode for the generated key.
    type: str
  type:
    description:
      - Key type (RSA, ECC, etc.).
    type: str
  state:
    description:
      - Whether the key should be present.
    type: str
    choices: [present, absent]
author:
  - Stub maintainer (@repo)
"""


EXAMPLES = r"""
- name: Generate a private key
  community.crypto.openssl_privatekey:
    path: /etc/pki/tls/private/server.key
    size: 4096
"""


RETURN = r"""
---
changed:
  description: Indicates whether any change was made.
  type: bool
  returned: always
"""


def run_module():
    module = AnsibleModule(
        argument_spec={
            "path": {"type": "path", "required": True},
            "size": {"type": "int", "required": False},
            "owner": {"type": "str", "required": False},
            "group": {"type": "str", "required": False},
            "mode": {"type": "str", "required": False},
            "type": {"type": "str", "required": False},
            "state": {"type": "str", "required": False, "choices": ["present", "absent"]},
        },
        supports_check_mode=True,
    )

    module.exit_json(changed=False)


def main():
    run_module()


if __name__ == "__main__":
    main()
