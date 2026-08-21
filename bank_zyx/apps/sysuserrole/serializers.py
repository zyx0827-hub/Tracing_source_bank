from rest_framework import serializers
from apps.sysuserrole.models import SysUserRole

class SysUserRoleSerializer(serializers.ModelSerializer):
    """用户表序列化"""
    class Meta:
        model = SysUserRole
        fields = '__all__'
        