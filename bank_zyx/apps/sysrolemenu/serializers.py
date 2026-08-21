from rest_framework import serializers
from apps.sysrolemenu.models import SysRoleMenu

class SysRoleMenuSerializer(serializers.ModelSerializer):
    """用户表序列化"""
    class Meta:
        model = SysRoleMenu
        fields = '__all__'
        