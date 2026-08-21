from rest_framework import serializers
from apps.tradeinfo.models import TradeInfo

class TradeInfoSerializer(serializers.ModelSerializer):
    """用户表序列化"""
    class Meta:
        model = TradeInfo
        fields = '__all__'
        