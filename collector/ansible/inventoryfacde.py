import json
from ansible.module_utils.six import iteritems


class InventoryFacade:
    """
    {"os":   {
                 "hosts":["192.168.119.131"]
            },
     "_meta": {
                 "hostvars": {"192.168.119.131": {"ansible_ssh_user": "", "ansible_ssh_pass": ""}}
             }
    }
    """

    def __init__(self, inventory, variable_manager, data):
        self.inventory = inventory
        self.variable_manager = variable_manager
        self.data = data
        self._host = set()
        self.parse()

    def parse(self):
        data_from_meta = None
        new_data = json.loads(self.data)
        for (group, gdata) in new_data.items():
            if group == '_meta':
                if 'hostvars' in gdata:
                    data_from_meta = gdata['hostvars']
            else:
                self.parse_group(group, gdata)
        for host in self._host:
            got = {}
            if data_from_meta is None:
                raise AttributeError("please set _meta attribute for host")
            else:
                got = data_from_meta.get(host, {})
            self.populate_host_vars([host], got)

    def parse_group(self, group, data):
        group = self.inventory.add_group(group)
        if not isinstance(data, dict):
            data = {'hosts': data}
        elif not any(k in data for k in ('hosts', 'vars', 'children')):
            data = {'hosts': [group], 'vars': data}

        if 'hosts' in data:
            if not isinstance(data['hosts'], list):
                raise AttributeError("group '%s' with bad data for the host list:\n %s" % (group, data))
            for hostname in data['hosts']:
                self._host.add(hostname)
                self.inventory.add_host(hostname, group)
        if 'vars' in data:
            if not isinstance(data['vars'], dict):
                raise AttributeError("group '%s' with bad data for variables:\n %s" % (group, data))
            for k, v in iteritems(data['vars']):
                self.inventory.set_variable(group, k, v)
        if group != '_meta' and isinstance(data, dict) and 'children' in data:
            for child_name in data['children']:
                child_name = self.inventory.add_group(child_name)
                self.inventory.add_child(group, child_name)

    def populate_host_vars(self, hosts, variables):
        for host in hosts:
            self.inventory.add_host(host)
            for k in variables:
                self.variable_manager.set_host_variable(host, k, variables[k])

    def get_inventory(self):
        return self.inventory

    def get_variable_manager(self):
        return self.variable_manager
