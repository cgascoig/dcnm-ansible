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
module: dcnm_network

short_description: Manage a network within Cisco DCNM

version_added: "2.4"

description:
    - "Manage a network within Cisco DCNM"

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
  network_name:
    description:
    - 'Network name within DCNM'
    required: yes
  network_id:
    description:
    - 'Network ID'
    required: yes
    type: int
  network_template:
    description:
    - 'Network template to use'
    required: no
    default: Default_Network_Universal
  network_extension_template:
    description:
    - 'Network extension template to use'
    required: no
    default: Default_Network_Extension_Universal
  network_template_config:
    description:
    - 'Configuration attributes passed to the Network and Network extension templates. See examples for minimal template config for default templates. '
    required: yes
    type: dict
  state:
    description:
    - 'Whether the network should exist within DCNM. If "present" will ensure the network is created. If "absent" will ensure the network is removed. '
    required: no
    default: present

author:
    - Chris Gascoigne (@cgascoig)
'''

EXAMPLES = '''
- name: create/update network
  dcnm_network:
    <<: *api_info
    fabric_name: test
    network_name: "MyNetwork_30000"
    vrf_name: MyVRF_50001
    network_id: 30000
    network_template_config:
        mcastGroup: "239.1.1.0"
        vrfName: "MyVRF_50001"
        nveId: "1"
        gatewayIpAddress: "10.3.3.1/24"
        segmentId: "30000"
        intfDescription: ""
        vlanName: ""
        secondaryGW1: ""
        secondaryGW2: ""
        vlanId: "300"
        networkName: "MyNetwork_30000"
        suppressArp: "true"
        isLayer2Only: "false"
        # mtu: ""
        # dhcpServerAddr1: ""
        # dhcpServerAddr2: ""
        # rtBothAuto: "false"
        # loopbackId: ""
        # gatewayIpV6Address: ""
        # vrfDhcp: ""
        # enableL3OnBorder: "false"
        # tag: "12345"
        # enableIR: "false"
        # trmEnabled: "false"
    state: present
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dcnm import DCNM, dcnm_argument_spec
import json

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dcnm_argument_spec
    module_args.update(
        fabric_name=dict(type='str', required=True),
        vrf_name=dict(type='str', required=True),
        network_name=dict(type='str', required=True),
        network_id=dict(type='int', required=True),
        network_template=dict(type='str', required=False, default="Default_Network_Universal"),
        network_extension_template=dict(type='str', required=False, default="Default_Network_Extension_Universal"),
        network_template_config=dict(type='dict', required=True),
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

        net = dcnm.get_net(module.params['fabric_name'], module.params['network_name'])

        # Handle state==absent cases
        if module.params['state'] == 'absent':
            if net is not None:
                # Network exists but shouldn't ... delete it
                if not module.check_mode:
                    dcnm.delete_net(module.params['fabric_name'], module.params['network_name'])
                result['changed'] = True
                module.exit_json(**result)
            else:
                module.exit_json(**result)

        # Handle state==present cases
        if net is not None:
            # Network already exists
            need_update = dcnm.compare_net_attrs(net, module.params)

            if need_update==False:
                module.exit_json(**result)

            result['comparejs']=net
            result['comparejs_templ']=json.loads(net['networkTemplateConfig'])
            # Update Network
            if not module.check_mode:
                net = dcnm.update_net(module.params)
            
            result['changed'] = True
            module.exit_json(**result)
            

        # Create Network        
        if not module.check_mode:
                net = dcnm.create_net(module.params)

        result['changed'] = True
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e), result=result)


def main():
    run_module()

if __name__ == '__main__':
    main()