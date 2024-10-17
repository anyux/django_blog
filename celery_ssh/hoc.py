from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from collections import namedtuple
from ansible import context
from ansible.module_utils.common.collections import ImmutableDict



# 自定义回调类以捕获详细结果
class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(f"{host.name} 成功: {result._result}")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host
        print(f"{host.name} 失败: {result._result}")

#在这里传递一些参数
context.CLIARGS = ImmutableDict(connection='ssh', module_path=None, verbosity=5,forks=10, become=None, become_method=None,become_user=None, check=False, diff=False,host_key_checking=False)
# play的执行对象和模块，这里设置hosts，其实是因为play把play_source和资产信息关联后，执行的play的时候它会去资产信息中设置的sources的hosts文件中

# 定义 play 源（临时剧本）
play_source = dict(
    name="Ansible Ad-hoc Command",
    hosts="192.168.255.182",  # 使用库存文件中的组名
    gather_facts="no",
    tasks=[
        dict(action=dict(module="ansible.builtin.ping", args=""))
    ]
)

# 初始化所需组件
dl = DataLoader()
im = InventoryManager(loader=dl, sources=["/etc/ansible/hosts"])  # 确保库存文件路径正确
vm = VariableManager(loader=dl, inventory=im)

# 定义选项
Options = namedtuple('Options',
                     ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user',
                      'check', 'diff', 'verbosity'])
options = Options(connection='ssh', module_path=None, forks=10, become=None,
                  become_method=None, become_user=None, check=False, diff=False, verbosity=0)

# 创建 play
play = Play().load(play_source, variable_manager=vm, loader=dl)

# 定义密码字典（如果需要）
passwords = {
    # 'ssh_password': 'your_password'  # 如果使用密码认证，取消注释并填写密码
}

# 创建回调实例
callback = ResultCallback()

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
    print(f"任务执行结果: {result}")
finally:
    if tqm is not None:
        tqm.cleanup()
