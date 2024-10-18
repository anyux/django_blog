from celery import shared_task
from celery.result import AsyncResult
from ansible_api.player import execplaybook
import time

@shared_task
def get_node_disk(inventory,yaml_path):
    result = execplaybook(inventory,yaml_path)
    return result
    # time.sleep(15)
    # return 1+2

@shared_task
def add(x=1,y=2):
    time.sleep(5)
    return x + y

def get_task_status(task_id):
    # 使用任务 ID 获取 Celery 任务结果
    result = AsyncResult(task_id)
    # 检查任务是否已完成
    if result.state == 'PENDING':
        response = {
            "state": result.state,
            "status": "Task is pending...",
        }
    elif result.state != 'FAILURE':
        response = {
            "state": result.state,
            "result": result.result,  # 获取任务结果
        }
    else:
        # 如果任务失败，返回错误信息
        response = {
            "state": result.state,
            "status": str(result.info),  # 返回错误信息
        }

    return response