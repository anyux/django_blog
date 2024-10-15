from django.http import JsonResponse

# Create your views here.
from .tasks import celery_ssh
from celery.result import AsyncResult

def task_cmd(request):
    cmd=request.GET.get('task_cmd','hostname')
    result = celery_ssh.delay(cmd)
    context = {
        "task_id":result.id,
    }
    return JsonResponse(context)

def task_status(request,task_id):
    # 使用任务 ID 获取 Celery 任务结果
    result = AsyncResult(task_id)
    print(result)
    print(result.state)
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

    return JsonResponse(response)