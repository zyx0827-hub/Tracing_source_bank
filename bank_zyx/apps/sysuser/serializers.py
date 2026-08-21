from rest_framework import serializers
from apps.sysuser.models import SysUser

class SysUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = '__all__'

# serializers.py
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = ['user_id', 'user_name', 'password', 'email', 'mobile', 'pid', 'address', 'is_active', 'create_time']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }
    
    def create(self, validated_data):
        # 在创建时处理密码
        user = SysUser.objects.create(**validated_data)
        return user