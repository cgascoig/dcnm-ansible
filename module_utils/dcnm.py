# Copyright: (c) 2018, Chris Gascoigne <cgascoig@cisco.com>


import requests

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
            print(vrf)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while deleting VRF: %s" % e)

    def create_vrf(self, module_params):
        body = self.generate_vrf_body(module_params)
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
        body = self.generate_vrf_body(module_params)
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

    VRF_ATTRS = {
        "vrfTemplate": "vrf_template",
        "vrfExtensionTemplate": "vrf_extension_template",
        "vrfTemplateConfig": "vrf_template_config",
        "vrfId": "vrf_id",
    }
    
    # return True if update needed
    def compare_vrf_attrs(self, js, yaml):
        # compare attributes
        need_update=False
        for jsattr, yamlattr in self.VRF_ATTRS.iteritems():
            if js[jsattr] != yaml[yamlattr]:
                need_update = True

        return need_update

    def generate_vrf_body(self, module_params):
        body=dict()
        for jsattr, yamlattr in self.VRF_ATTRS.iteritems():
            body[jsattr] = module_params[yamlattr]
        
        return body