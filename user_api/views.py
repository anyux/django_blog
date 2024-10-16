from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
import logging

from .serializers import UserSerializer, DiskInfoSerializer
from user_api.models import User
from celery_ssh.tasks import celery_ssh
from celery.result import AsyncResult

# 获取 logger
logger = logging.getLogger('ansible_tasks')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class DiskInfoViewSet(APIView):
    def post(self, request,*args, **kwargs):
        # 获取请求中传递的参数
        command = request.data.get('command', None)

        if not command:
            return Response({"error": "No command provided."}, status=status.HTTP_400_BAD_REQUEST)

        # 启动 Celery 任务来获取磁盘信息
        task = celery_ssh.delay(command)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    def get(self, request,task_id,*args, **kwargs):
        # 通过任务ID获取任务的状态和结果
        print(task_id)
        task_result = AsyncResult(task_id)

        if task_result.state == 'PENDING':
            return Response({"status": "Task is still pending."}, status=status.HTTP_202_ACCEPTED)

        elif task_result.state == 'SUCCESS':

            # 获取磁盘信息
            disk_info_data = task_result.result

            # 序列化磁盘信息
            serializer = DiskInfoSerializer(disk_info_data, many=True)
            return Response({"status": "Task completed", "result": serializer.data}, status=status.HTTP_200_OK)

        elif task_result.state == 'FAILURE':
            return Response({"status": "Task failed", "error": str(task_result.info)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"status": task_result.state}, status=status.HTTP_202_ACCEPTED)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery_ssh.tasks import run_ansible_playbook

class RunPlaybookView(APIView):
    def post(self, request, *args, **kwargs):
        playbook_path = request.data.get('playbook_path')
        inventory = request.data.get('inventory')
        extra_vars = request.data.get('extra_vars', {})

        if not playbook_path or not inventory:
            return Response({"error": "playbook_path and inventory are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 调用 Celery 任务异步执行 Ansible Playbook
        task = run_ansible_playbook.delay(playbook_path, inventory, extra_vars)

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


# views.py
from celery.result import AsyncResult

class TaskStatusView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        task_result = AsyncResult(task_id)

        if task_result.state == 'PENDING':
            return Response({"status": "Task is still pending."}, status=status.HTTP_200_OK)
        elif task_result.state == 'SUCCESS':
            return Response({"status": "Task completed", "result": task_result.result}, status=status.HTTP_200_OK)
        elif task_result.state == 'FAILURE':
            return Response({"status": "Task failed", "error": str(task_result.info)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status": task_result.state}, status=status.HTTP_200_OK)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery_ssh.tasks import run_ansible_ad_hoc

class RunAdHocCommandView(APIView):
    def post(self, request, *args, **kwargs):
        module_name = request.data.get('module_name', 'ping')  # 默认使用 ping 模块
        module_args = request.data.get('module_args', '')
        hosts = request.data.get('hosts', 'all')  # 默认运行在所有主机
        # 记录请求
        logger.info(f"Received Ad-hoc command request: module={module_name}, args={module_args}, hosts={hosts}")

        if not module_name:
            logger.error("module_name is missing in the request.")

            return Response({"error": "module_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 调用 Celery 任务，异步执行 Ad-hoc 命令
        try:
            task = run_ansible_ad_hoc.delay(module_name, module_args, hosts)
            logger.info(f"Ansible task dispatched successfully, task_id={task.id},module_name={module_name},module_args={module_args},hosts={hosts}")
            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"Error dispatching Ansible task: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
