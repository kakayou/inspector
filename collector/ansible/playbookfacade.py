from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.module_utils.six import iteritems
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible import context

from collector.ansible.callbackfacade import CallBackFacade
from collector.ansible.inventoryfacde import InventoryFacade


class PlayBook:
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, callback):
        self.callback = callback

    def run(self, playbook, json_data, extra_vars):
        """
        run ansible palybook
        """
        context.CLIARGS = ImmutableDict(
            connection='smart',
            remote_user=None,
            ack_pass=None,
            become=None,
            become_method=None,
            become_user=None,
            sudo=None,
            sudo_user=None,
            ask_sudo_pass=None,
            module_path=None,
            check=False,
            verbosity=5,
            listhosts=None,
            listtasks=None,
            listtags=None,
            syntax=None,
            start_at_task=None,
            ask_vault_pass=False,
            private_key_file=None,
            timeout=10,
            forks=3
        )

        loader = DataLoader()
        passwords = dict()
        inventory = InventoryManager(loader=loader, sources=None)
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        json_parse = InventoryFacade(inventory=inventory, variable_manager=variable_manager, data=json_data)
        new_inventory = json_parse.get_inventory()
        variable_manager = json_parse.get_variable_manager()

        try:
            if self.callback is None:
                playbook_callback = CallBackFacade()
            else:
                playbook_callback = self.callback
            filenames = [playbook]
            # --extra-vars 指定的的参数
            if isinstance(extra_vars, dict):
                for k, v in iteritems(extra_vars):
                    variable_manager.extra_vars[k] = v
            # actually run it
            executor = PlaybookExecutor(
                playbooks=filenames, inventory=new_inventory, variable_manager=variable_manager,
                loader=loader, passwords=passwords)
            executor._tqm._stdout_callback = playbook_callback
            executor.run()
        except Exception as e:
            raise Exception(e)
