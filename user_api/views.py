from celery.result import AsyncResult
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from .serializers import UserSerializer
from rest_framework.views import APIView
from user_api.models import User
from app1.tasks import count_user
from celery.result import AsyncResult
from django.http import JsonResponse
class UserviewAPIView(APIView):
    def get(self, request,pk=None):
        if pk is None:
            # serializer = UserSerializer(request.user)
            # return Response(serializer.data)
            queryset = User.objects.all()
            serializer = UserSerializer(queryset, many=True)
            print(serializer)
            print(serializer.data)
        else:
            queryset = User.objects.get(pk=pk)
            serializer = UserSerializer(queryset)
            print(serializer)
            print(serializer.data)

        return Response(serializer.data)
    def post(self, request):
        #获取post数据
        data= request.data
        # 调用序列化器将提交的数据进行反序列化
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            msg = "ok"
            code=200
        else:
            msg=serializer.errors
            code=400
        response={'msg':msg,'code':code}
        return Response(response)
    def put(self, request,pk=None):
        # 获取json数据
        data= request.data
        # 获取主键对象
        user = User.objects.get(pk=pk)
        # 调用序列化器将提交的数据进行反序列化
        serializer = UserSerializer(instance=user,data=data)
        if serializer.is_valid():
            # 调用 update方法
            serializer.save()
            msg = "ok"
            code=200
        else:
            msg=serializer.errors
            code=400
        response={'msg':msg,'code':code}
        return Response(response)
    def delete(self, request,pk=None):
        try:
            User.objects.get(id=pk).delete()
            msg = "ok"
            code=200
        except Exception as e:
            msg=str(e)
            code=400
        response={'msg':msg,'code':code}
        return Response(response)


class app1viewAPIView(APIView):
    def get(self, request):
        queryset = count_user.delay()
        # serializer = UserSerializer(queryset.get(), many=True)
        # print(serializer)
        # print(serializer.data)
        # return Response(serializer.data)
        return JsonResponse({'task_id':queryset.id})

class app2viewAPIView(APIView):

    def get(self,request, pk=None ):
        result = AsyncResult(pk)  # 通过任务 ID 获取任务状态

        if result.state == 'PENDING':
            return JsonResponse({'status': 'Task is still running'})
        elif result.state == 'SUCCESS':
            return JsonResponse({
                'status': 'Task completed',
                'result': result.result  # 返回包含 task_id 的查询结果
            })
        elif result.state == 'FAILURE':
            return JsonResponse({'status': 'Task failed', 'error': str(result.info)})