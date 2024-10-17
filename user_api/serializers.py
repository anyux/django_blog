from user_api.models import User
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    age = serializers.CharField(max_length=100)
    sex = serializers.CharField(max_length=100)

    # 重写create()方法,实现数据写入
    def create(self, validated_data):
        # validated_data 反序列化后的数据
        return User.objects.create(**validated_data)

    # 重写update()方法,实现数据更新
    def update(self, instance, validated_data):
        # instance是当前操作对象,validated_data是反序列化后的结果
        instance.name = validated_data.get('name', instance.name)
        instance.city = validated_data.get('city', instance.city)
        instance.age = validated_data.get('age', instance.age)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.save()
        return instance