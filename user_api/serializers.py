from user_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class DiskInfoSerializer(serializers.Serializer):
    device = serializers.CharField(max_length=100)
    mountpoint = serializers.CharField(max_length=100)
    fstype = serializers.CharField(max_length=10)
    total = serializers.IntegerField()
    used = serializers.IntegerField()
    free = serializers.IntegerField()
    percent = serializers.FloatField()
