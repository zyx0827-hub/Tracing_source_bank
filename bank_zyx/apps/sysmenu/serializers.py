from rest_framework import serializers
from apps.sysmenu.models import SysMenu

class SysMenuSerializer(serializers.ModelSerializer):
    """用户表序列化"""
    class Meta:
        model = SysMenu
        fields = '__all__'
        