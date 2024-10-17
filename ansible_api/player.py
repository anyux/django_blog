#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
#from collections import namedtuple
# 核心类
# 用于读取YAML和JSON格式的文件
from ansible.parsing.dataloader import DataLoader
# 用于存储各类变量信息
from ansible.vars.manager import VariableManager
# 用于导入资产文件
from ansible.inventory.manager import InventoryManager
# 操作单个主机信息
from ansible.inventory.host import Host
# 操作单个主机组信息
from ansible.inventory.group import Group
# 存储执行hosts的角色信息
from ansible.playbook.play import Play
# ansible底层用到的任务队列
from ansible.executor.task_queue_manager import TaskQueueManager
# 核心类执行playbook
from ansible.executor.playbook_executor import PlaybookExecutor
# 状态回调，各种成功失败的状态
from ansible.plugins.callback import CallbackBase
# 新增下面两个调用
from ansible.module_utils.common.collections import ImmutableDict
from ansible import context

class ResultsCollectorJSONCallback(CallbackBase):
    """
    playbook的callback改写，格式化输出playbook执行结果, 支持多个任务的结果收集
    """
    CALLBACK_VERSION = 2.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_unreachable = {}
        self.task_failed = {}
        self.task_skipped = {}
        self.task_status = {}

    def v2_runner_on_unreachable(self, result):
        """
        重写 unreachable 状态
        :param result:  这是父类里面一个对象，这个对象可以获取执行任务信息
        """
        host = result._host.get_name()
        self.task_unreachable.setdefault(host, []).append(result._result)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """
        重写 ok 状态，支持多个任务
        :param result:
        """
        host = result._host.get_name()
        task_name = result.task_name
        if host not in self.task_ok:
            self.task_ok[host] = []
        self.task_ok[host].append({
            'task': task_name,
            'result': result._result
        })

    def v2_runner_on_failed(self, result, *args, **kwargs):
        """
        重写 failed 状态，支持多个任务
        :param result:
        """
        host = result._host.get_name()
        task_name = result.task_name
        if host not in self.task_failed:
            self.task_failed[host] = []
        self.task_failed[host].append({
            'task': task_name,
            'result': result._result
        })

    def v2_runner_on_skipped(self, result):
        host = result._host.get_name()
        task_name = result.task_name
        if host not in self.task_skipped:
            self.task_skipped[host] = []
        self.task_skipped[host].append({
            'task': task_name,
            'result': result._result
        })

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            self.task_status[h] = {
                "ok": t["ok"],
                "changed": t["changed"],
                "unreachable": t["unreachable"],
                "skipped": t["skipped"],
                "failed": t["failures"]
            }




def execplaybook():
    """
    调用playbook，获取所有任务结果
    """
    # 资产配置信息
    DL = DataLoader()
    IM = InventoryManager(loader=DL, sources="/etc/ansible/hosts")
    VM = VariableManager(loader=DL, inventory=IM)

    # 执行选项
    context.CLIARGS = ImmutableDict(connection='ssh', module_path=None, verbosity=5,forks=10, become=None, become_method=None,become_user=None, check=False, diff=False,host_key_checking=False,syntax=None,start_at_task=None)
    passwords = dict()  # 这个可以为空，因为在hosts文件中,而且一般也是秘钥登录

    # playbooks参数里面放的就是playbook文件路径
    playbook = PlaybookExecutor(playbooks=["/etc/ansible/cpu.yml"], inventory=IM, variable_manager=VM, loader=DL, passwords=passwords)
    callback = ResultsCollectorJSONCallback()
    playbook._tqm._stdout_callback = callback  # 配置callback
    playbook.run()

    result_raw = {"ok": {}, "failed": {}, "unreachable": {}, "skipped": {}, "status": {}}

    # 获取所有成功的任务结果
    for host, results in callback.task_ok.items():
        result_raw["ok"][host] = []
        for result in results:
            result_raw["ok"][host].append({
                'task': result['task'],
                'stdout': result['result'].get('stdout', ''),
                'stderr': result['result'].get('stderr', ''),
                'changed': result['result'].get('changed', False)
            })

    # 获取所有失败的任务结果
    for host, results in callback.task_failed.items():
        result_raw["failed"][host] = []
        for result in results:
            result_raw["failed"][host].append({
                'task': result['task'],
                'msg': result['result'].get('msg', ''),
                'stdout': result['result'].get('stdout', ''),
                'stderr': result['result'].get('stderr', '')
            })

    # 获取所有不可达的任务结果
    for host, results in callback.task_unreachable.items():
        result_raw["unreachable"][host] = []
        for result in results:
            result_raw["unreachable"][host].append(result)

    # 获取所有跳过的任务结果
    for host, results in callback.task_skipped.items():
        result_raw["skipped"][host] = []
        for result in results:
            result_raw["skipped"][host].append(result)

    return result_raw


if __name__ == '__main__':
    execplaybook()
