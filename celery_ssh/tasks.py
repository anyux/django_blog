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

