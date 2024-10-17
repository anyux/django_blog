from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible import context
from ansible.module_utils.common.collections import ImmutableDict
import json

# 创建一个回调插件，以便我们可以捕获输出
class ResultsCollectorJSONCallback(CallbackBase):
    """一个示例回调插件，用于在结果出现时执行操作。如果要将所有结果收集到单个对象中，以在执行结束时进行处理，请考虑使用json回调插件或编写自己的自定义 回调插件。
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """打印结果的json表示形式。另外，将结果存储在实例属性中，以供以后检索"""
        host = result._host
        self.host_ok[host.get_name()] = result
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result




# 定义 play 源
play_source = dict(
    name="Ansible Ad-hoc Command",
    hosts="192.168.255.182",  # 使用库存文件中的组名
    gather_facts="yes",
    tasks=[
        dict(action=dict(module="ansible.builtin.shell", args="df -h"))
    ]
)

# 初始化所需组件
dl = DataLoader()
im = InventoryManager(loader=dl, sources=["/etc/ansible/hosts"])
vm = VariableManager(loader=dl, inventory=im)

# # 定义选项
# Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become',
#                                  'become_method', 'become_user', 'check', 'diff', 'verbosity'])
# options = Options(connection='ssh', module_path=None, forks=10, become=None,
#                   become_method=None, become_user=None, check=False, diff=False, verbosity=0)
# 设置 CLI 参数
context.CLIARGS = ImmutableDict(
    connection='ssh', module_path=None, verbosity=0, forks=10, become=None,
    become_method=None, become_user=None, check=False, diff=False, host_key_checking=False
)
# 创建 play
play = Play().load(play_source, variable_manager=vm, loader=dl)

# 定义密码字典（如果需要）
passwords = {
    # 'ssh_password': 'your_password'  # 如果使用密码认证，取消注释并填写密码
}

# 创建回调实例
callback = ResultsCollectorJSONCallback()

# 创建 TaskQueueManager 并执行 play
tqm = None
try:
    tqm = TaskQueueManager(
        inventory=im,
        variable_manager=vm,
        loader=dl,
        passwords=passwords,
        stdout_callback=callback  # 使用自定义回调类
    )
    result = tqm.run(play)
finally:
    if tqm is not None and hasattr(tqm, 'cleanup'):
        tqm.cleanup()
