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
module: dcnm_vrf

short_description: Manage a VRF within Cisco DCNM

version_added: "2.4"

description:
    - "Manage a VRF within Cisco DCNM"

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
  fabric_name:
    description:
    - 'Fabric name with DCNM'
    required: yes
  vrf_name:
    description:
    - 'VRF name within DCNM'
    required: yes
  vrf_template:
    description:
    - 'VRF template to use'
    required: no
    default: Default_VRF_Universal
  vrf_extension_template:
    description:
    - 'VRF extension template to use'
    required: no
    default: Default_VRF_Extension_Universal
  vrf_template_config:
    description:
    - 'Configuration attributes passed to the VRF and VRF extension templates. See examples for minimal template config for default templates. '
    required: yes
    type: dict
  vrf_id:
    description:
    - 'VRF ID'
    required: yes
    type: int
  state:
    description:
    - 'Whether the VRF should exist within DCNM. If "present" will ensure the VRF is created. If "absent" will ensure the VRF is removed. '
    required: no
    default: present

author:
    - Chris Gascoigne (@cgascoig)
'''

EXAMPLES = '''
- name: create/update VRF
  dcnm_vrf:
    <<: *api_info
    fabric_name: MyFabric
    vrf_name: MyVRF_50001
    vrf_template_config: 
        nveId: "1"
        vrfVlanId: "3"
        asn: "65500"
        vrfName: "MyVRF_50001"
        vrfSegmentId: "50001"
    vrf_id: 50001
    state: present
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dcnm import DCNM, dcnm_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dcnm_argument_spec
    module_args.update(
        fabric_name=dict(type='str', required=True),
        vrf_name=dict(type='str', required=True),
        vrf_template=dict(type='str', required=False, default="Default_VRF_Universal"),
        vrf_extension_template=dict(type='str', required=False, default="Default_VRF_Extension_Universal"),
        vrf_template_config=dict(type='dict', required=True),
        vrf_id=dict(type='int', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),

    )

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

        vrf = dcnm.get_vrf(module.params['fabric_name'], module.params['vrf_name'])

        # Handle state==absent cases
        if module.params['state'] == 'absent':
            if vrf is not None:
                # VRF exists but shouldn't ... delete it
                if not module.check_mode:
                    dcnm.delete_vrf(module.params['fabric_name'], module.params['vrf_name'])
                result['changed'] = True
                module.exit_json(**result)
            else:
                module.exit_json(**result)

        # Handle state==present cases
        if vrf is not None:
            # VRF already exists
            need_update = dcnm.compare_vrf_attrs(vrf, module.params)

            if need_update==False:
                module.exit_json(**result)

            # Update VRF
            if not module.check_mode:
                vrf = dcnm.update_vrf(module.params)
            
            result['changed'] = True
            module.exit_json(**result)
            

        # Create VRF        
        if not module.check_mode:
                vrf = dcnm.create_vrf(module.params)

        result['changed'] = True
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e), result=result)

def main():
    run_module()

if __name__ == '__main__':
    main()