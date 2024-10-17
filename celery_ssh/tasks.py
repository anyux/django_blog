import json

import paramiko
import logging
from celery import shared_task
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from collections import namedtuple
# 获取 logger
logger = logging.getLogger('ansible_tasks')

# tasks.py


@shared_task
def celery_ssh(cmd):
    # 创建SSH客户端n
    ssh_client = paramiko.SSHClient()
    # 自动接受未知的SSH密钥（不推荐用于生产环境）
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 使用用户名、密码登录到远程服务器
    ssh_client.connect(hostname="192.168.255.181", username="root", password="Ts@z*lih34")

    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    # 获取命令输出
    output = stdout.read().decode("utf-8")

    return output


@shared_task
def run_ansible_playbook(playbook_path,inventory,extra_vars=None):
    """
    运行 Ansible playbook 的 Celery 任务
    :param playbook_path: 要运行的 playbook 文件路径
    :param inventory: Ansible 主机清单文件路径
    :param extra_vars: 额外的变量
    :return: 任务结果
    """
    result = ansible_runner.run(
        private_data_dir='/tmp/',  # 临时目录用于 Ansible 数据存储
        playbook=playbook_path,
        inventory=inventory,
        extravars=extra_vars
    )
    return result.stats  # 返回任务的统计信息

@shared_task
def run_ansible_ad_hoc(module_name, module_args, hosts):
    """
    运行 Ansible Ad-hoc 命令的 Celery 任务，支持记录日志
    :param module_name: Ansible 模块名称 (如 'ping')
    :param module_args: 模块参数 (如 'data=test')
    :param hosts: 目标主机 (如 'all')
    :return: 返回任务的执行结果
    """
    # 记录任务启动
    logger.info(f"Starting Ansible Ad-hoc Task with module: {module_name}, args: {module_args}, hosts: {hosts}")

    # 加载 Ansible 相关配置
    loader = DataLoader()  # 数据加载器
    inventory = InventoryManager(loader=loader, sources=['/tmp/hosts'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    # 定义一个 Play 任务
    play_source = dict(
        name='Ansible Play',
        hosts='192.168.255.182',
        gather_facts='yes',
        tasks=[{
            'action': {
                'module': 'shell',
                'args':"ls /tmp"
            }
        }]
    )

    logger.info(f'{play_source}')

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # 使用自定义回调类来收集结果
    callback = ResultCallback()

    # 创建 TaskQueueManager 管理任务
    Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
    options = Options(connection='ssh', module_path=None, forks=10, become=None, become_method=None, become_user=None, check=False)

    passwords = dict()

    # 执行 Ad-hoc 任务
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords=passwords,
        stdout_callback=callback  # 设置我们的自定义 callback
    )

    try:
        tqm.run(play)  # 运行任务
    except Exception as e:
        logger.error(f"Error running Ansible task: {str(e)}")
    finally:
        tqm.cleanup()  # 清理

    # 记录任务结束
    logger.info(f"Finished Ansible Ad-hoc Task for module: {module_name} on hosts: {hosts}")

    return callback.results  # 返回执行结果


# 主要任务函数
def adhoc():
    # 资产配置信息
    dl = DataLoader()
    im = InventoryManager(loader=dl, sources=["/tmp/hosts"])  # 确保正确的路径
    vm = VariableManager(loader=dl, inventory=im)

    # 执行对象和模块
    play_source = dict(
        name="Ansible Ad-hoc Command",
        hosts="all",  # 或者指定具体主机
        gather_facts="no",
        tasks=[
            dict(action=dict(module="shell", args="ls /tmp"))
        ]
    )

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

    try:
        result = tqm.run(play)
        # 这里可以处理结果
        print(json.dumps([res._result for res in callback.results], indent=4))
    finally:
        tqm.cleanup()

    return result