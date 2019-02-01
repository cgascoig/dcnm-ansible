#!/usr/bin/python
# -*- coding: utf-8 -*-
"""dcnm_facts module

Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"
__author__ = "Chris Gascoigne"

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: dcnm_facts

short_description: Gather facts from Cisco DCNM

version_added: "2.4"

description:
    - "Gather facts from Cisco DCNM"

options:
  baseurl:
    description:
    - 'The base URL of the DCNM REST API. Usually of the form https://<DCNM_API>/rest'
    required: yes
  username:
    description:
    - 'Username for DCNM API'
    required: yes
  password:
    description:
    - 'Password for DCNM API'
    required: yes
  verify:
    description:
    - 'Verify SSL certificates of DCNM REST API.'
    required: no
    type: bool
    default: yes

author:
    - Chris Gascoigne (@cgascoig)
'''

EXAMPLES = '''
- name: Gather facts from DCNM
  dcnm_facts:
    baseurl: https://10.1.1.1/rest
    username: admin
    password: password
    verify: no
'''

RETURN = '''
dcnm_fabrics:
    description: The facts retrieved from DCNM
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dcnm import DCNM, dcnm_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dcnm_argument_spec

    # seed the result dict
    result = dict(
        changed=False,
        ansible_facts=dict()
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )


    try:
        dcnm = DCNM(module.params['baseurl'], module.params['username'], module.params['password'], verify=module.params['verify'])

        dcnm.login()
        result['ansible_facts']['dcnm_fabrics'] = dcnm.request("GET", "/control/fabrics")

        # successful execution
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e))

def main():
    run_module()

if __name__ == '__main__':
    main()