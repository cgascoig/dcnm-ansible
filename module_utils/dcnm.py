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

import requests
import sys
import json

dcnm_argument_spec = dict(
    baseurl=dict(type='str', required=True),
    username=dict(type='str', required=True),
    password=dict(type='str', required=True, no_log=True),
    verify=dict(type='bool', required=False, default=True),
)

class DCNM(object):
    def __init__(self, baseurl, username, password, verify=True):
        self.username = username
        self.password = password
        self.verify = verify
        self.baseurl = baseurl
        self.token=None

    def get_url(self, endpoint):
        return self.baseurl + endpoint

    def login(self):
        payload = "{'expirationTime': 60000}"
        body = {
            'expirationTime': 60000
        }
        headers = {
            'Content-Type': "application/json",
        }

        auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        url = self.get_url("/logon")

        try:
            response = requests.request("POST", url, auth=auth, json=body, headers=headers, verify=self.verify)

            js = response.json()
            self.token = js["Dcnm-Token"]

            print("DCNM authenticated, token %s"%self.token)
        except Exception as e:
            raise Exception("An error occurred while authenticating to DCNM: %s"%e)
            return None
        
        return self.token

    def request(self, method, endpoint, json=None):
        url = self.get_url(endpoint)
        headers = {
            'Dcnm-Token': self.token
        }
        try:
            response = requests.request(method, url, json=json, headers=headers, verify=self.verify)

            if not response.ok:
                raise Exception("%s: %s"%(response.reason, response.text))

            try:
                ret=response.json()
            except ValueError:
                ret=None

            return ret
        except Exception as e:
            raise Exception("An error has occurred while sending request to DCNM: %s" % e)
            return None

    #################################
    # VRF related methods
    #################################
    def get_vrf(self, fabric_name, vrf_name):
        if self.token is None:
            raise Exception("Attempt to get VRF info before authentication")

        try:
            vrf=self.request("GET", "/top-down/fabrics/%s/vrfs/%s"%(fabric_name, vrf_name))
            return vrf
        except:
            # assume any exception means the VRF doesn't exist
            return None

    def delete_vrf(self, fabric_name, vrf_name):
        if self.token is None:
            raise Exception("Attempt to delete VRF before authentication")

        try:
            vrf=self.request("DELETE", "/top-down/fabrics/%s/vrfs/%s"%(fabric_name, vrf_name))
            return vrf
        except Exception as e:
            raise Exception("An error occurred while deleting VRF: %s" % e)

    def create_vrf(self, module_params):
        body = self.generate_body(module_params, self.VRF_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrfName=module_params['vrf_name'],
        )

        if self.token is None:
            raise Exception("Attempt to create VRF info before authentication")
        
        try:
            vrf = self.request("POST", "/top-down/fabrics/%s/vrfs"%module_params['fabric_name'], json=body)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while creating VRF: %s"%e)
    
    def update_vrf(self, module_params):
        body = self.generate_body(module_params, self.VRF_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrfName=module_params['vrf_name'],
        )

        if self.token is None:
            raise Exception("Attempt to update VRF info before authentication")
        
        try:
            vrf = self.request("PUT", "/top-down/fabrics/%s/vrfs/%s"%(module_params['fabric_name'], module_params['vrf_name']), json=body)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while updating VRF: %s"%e)

    # return True if update needed
    def compare_vrf_attrs(self, js, yaml):
        return self.compare_attrs(js, yaml, self.VRF_ATTRS)

    VRF_ATTRS = {
        "vrfTemplate": "vrf_template",
        "vrfExtensionTemplate": "vrf_extension_template",
        "vrfTemplateConfig": "vrf_template_config",
        "vrfId": "vrf_id",
    }

    #################################
    # Network related methods
    #################################

    def get_net(self, fabric_name, net_name):
        if self.token is None:
            raise Exception("Attempt to get network info before authentication")

        try:
            net=self.request("GET", "/top-down/fabrics/%s/networks/%s"%(fabric_name, net_name))
            return net
        except:
            # assume any exception means the network doesn't exist
            return None

    def delete_net(self, fabric_name, net_name):
        if self.token is None:
            raise Exception("Attempt to delete network before authentication")

        try:
            net=self.request("DELETE", "/top-down/fabrics/%s/networks/%s"%(fabric_name, net_name))
            return net
        except Exception as e:
            raise Exception("An error occurred while deleting network: %s" % e)

    def create_net(self, module_params):
        body = self.generate_body(module_params, self.NET_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrf=module_params['vrf_name'],
            networkName=module_params['network_name'],
        )

        if self.token is None:
            raise Exception("Attempt to create network info before authentication")
        
        try:
            net = self.request("POST", "/top-down/fabrics/%s/networks"%module_params['fabric_name'], json=body)
            return net
        except Exception as e:
            raise Exception("An error occurred while creating network: %s"%e)
    
    def update_net(self, module_params):
        body = self.generate_body(module_params, self.NET_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrf=module_params['vrf_name'],
            networkName=module_params['network_name'],
        )

        if self.token is None:
            raise Exception("Attempt to update network info before authentication")
        
        try:
            net = self.request("PUT", "/top-down/fabrics/%s/networks/%s"%(module_params['fabric_name'], module_params['network_name']), json=body)
            return net
        except Exception as e:
            raise Exception("An error occurred while updating network: %s"%e)

    # return True if update needed
    def compare_net_attrs(self, js, yaml):
        return self.compare_attrs(js, yaml, self.NET_ATTRS)

    NET_ATTRS = {
        "networkTemplate": "network_template",
        "networkExtensionTemplate": "network_extension_template",
        "networkTemplateConfig": "network_template_config",
        "networkId": "network_id",
    }

    #################################
    # Genric utility methods
    #################################
    
    # return True if update needed
    def compare_attrs(self, js, yaml, attrmap):
        need_update=False
        for jsattr, yamlattr in attrmap.iteritems():
            if type(yaml[yamlattr]) is dict:
                # if the attribute in the yaml is a dict, parse the json attribute as json
                # this handles the vrfTemplateConfig and networkTemplateConfig attributes which are actually JSON encoded strings in the API
                if json.loads(js[jsattr]) != yaml[yamlattr]:
                    need_update = True
            else:
                if js[jsattr] != yaml[yamlattr]:
                    need_update = True

        return need_update

    def generate_body(self, module_params, attrmap):
        body=dict()
        for jsattr, yamlattr in attrmap.iteritems():
            # if the attribute in the module_params is a dict, dump the attribute as json
            # this handles the vrfTemplateConfig and networkTemplateConfig attributes which are actually JSON encoded strings in the API
            if type(module_params[yamlattr]) is dict:
                body[jsattr] = json.dumps(module_params[yamlattr])
            else:
                body[jsattr] = module_params[yamlattr]
        
        return body