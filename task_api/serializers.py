from rest_framework import serializers
from task_api.models import Task,TaskRun

class TaskSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=100)
    # task_result = serializers.JSONField(default={})
    task_result = serializers.CharField(max_length=20000)

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

class TaskRunSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=36)
    task_name = serializers.CharField(max_length=36)
    task_inventory = serializers.CharField(max_length=100)
    task_yamlpath = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return TaskRun.objects.create(**validated_data)