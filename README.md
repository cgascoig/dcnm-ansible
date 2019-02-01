# Cisco DCNM Ansible Module

## Installation

Ansible must be installed. 

Clone this repository:
```
git clone https://github.com/cgascoig/dcnm-ansible
```

## Usage

Create a playbook, like this example:

```yaml

---
- name: test dcnm module
  hosts: localhost
  vars:
    api_info: &api_info
      baseurl: https://10.67.28.160/rest
      username: admin
      password: "C1sco123!!"
      verify: no
  tasks:
    - name: dcnm_facts
      dcnm_facts:
        <<: *api_info

    - name: output fabrics
      debug:
        msg: "Fabric name: {{ item.fabricName }}"
      loop: "{{ ansible_facts.dcnm_fabrics }}"

    - name: create/update VRF
      dcnm_vrf:
        <<: *api_info
        fabric_name: test
        vrf_name: MyVRF_50001
        vrf_template_config: 
          nveId: "1"
          vrfVlanId: "3"
          asn: "65500"
          vrfName: "MyVRF_50001"
          vrfSegmentId: "50001"
        vrf_id: 50001
        state: present

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

```

The Ansible modules closely mirror the DCNM REST API for top-down network provisioning so look at the API documentation for more details on the parameters: https://<DCNM_IP>/api-docs/

Execute playbook:

```
ansible-playbook test-playbook.yml
```
