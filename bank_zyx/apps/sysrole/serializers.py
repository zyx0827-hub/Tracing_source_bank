from rest_framework import serializers
from apps.sysrole.models import SysRole

class SysRoleSerializer(serializers.ModelSerializer):
    """用户表序列化"""
    class Meta:
        model = SysRole
        fields = '__all__'
        