from ansible.parsing.dataloader import DataLoader

# 装置主机配置清单类
from ansible.inventory.manager import InventoryManager

#装置工具
loader = DataLoader()

#加载主机配置清单
inventory = InventoryManager(loader=loader,sources=['/etc/ansible/hosts'])

#添加主机到指定主机组
inventory.add_host(host="1.1.1.1",port=222,group='test2')
#查看主机组资源
inventory.get_groups_dict()
#获取指定的主机对象
inventory.get_host(hostname="1.1.1.1")


#主机变量管理
from ansible.vars.manager import VariableManager

#获取变量实例
Variable_manager = VariableManager(loader=loader,inventory=inventory)

#查看变量方法
host=inventory.get_host(hostname='192.168.255.8')
Variable_manager.get_vars(host=host)
#设置主机变量方法,这里无法修改变量,
host=inventory.get_host(hostname='192.168.255.8')
Variable_manager.set_host_variable(host=host,varname='ansible_ssh_user',value="123456")
Variable_manager.get_vars()
#添加扩展变量
# extra_vars = {'some_variable': 'some_value', 'another_variable': 'another_value'}
# variable.extra_vars.update(extra_vars)

# Variable_manager.extra_vars={"web":"qq.com","site":"tx"}


#导入运行类
from ansible.playbook.play import Play

#导入tuple类型
from collections import namedtuple

#导入任务队列类
from ansible.executor.task_queue_manager import TaskQueueManager

#导入回调类
from ansible.plugins.callback import CallbackBase

# 执行对象和模块
play_source = dict(
    name="Ansible Ad-hoc Command",
    hosts="localhost",  # 或者指定具体主机
    gather_facts="no",
    tasks=[
        dict(action=dict(module="ansible.builtin.command", args="ls /tmp"))
    ]
)

dl = DataLoader()
im = InventoryManager(loader=dl, sources=["/etc/ansible/hosts"])  # 确保正确的路径
vm = VariableManager(loader=dl, inventory=im)

# 定义选项（模拟命令行参数）
Options = namedtuple('Options', 
    ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 
     'check', 'diff', 'verbosity'])

# 设定 options 的值
options = Options(connection='ssh', module_path=None, forks=10, become=None, 
                  become_method=None, become_user=None, check=False, diff=False, verbosity=3)


# 定义 play
play = Play().load(play_source, variable_manager=vm, loader=dl)

# 定义空密码字典
passwords = dict()

# 创建 TaskQueueManager，并传入必要的参数
callback = CallbackBase()  # 使用自定义的回调类来捕获结果
tqm = TaskQueueManager(
    inventory=im,
    variable_manager=vm,
    loader=dl,
    passwords=passwords,
    stdout_callback=callback  # 回调对象
)


result = tqm.run(play)

#导入playbook运行类
#from ansible.executor.playbook_executor import PlaybookExecutor
