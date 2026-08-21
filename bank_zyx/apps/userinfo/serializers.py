from rest_framework import serializers
from apps.userinfo.models import UserInfo
# apps/userinfo/serializers.py
# serializers.py
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'
    
    def create(self, validated_data):
        # 移除自动生成customer_id的逻辑，让Django自动处理
        return super().create(validated_data)