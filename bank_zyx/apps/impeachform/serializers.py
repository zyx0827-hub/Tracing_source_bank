from rest_framework import serializers
from apps.impeachform.models import ImpeachForm



class impeachformSerializer(serializers.ModelSerializer):
    """用户表序列化"""
    class Meta:
        model = ImpeachForm
        fields = '__all__'
        