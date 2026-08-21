# File: apps/audit/serializers.py
from rest_framework import serializers
from apps.audit.models import Audit

class AuditSerializer(serializers.ModelSerializer):
    """审计表序列化器"""
    # 添加只读字段用于前端显示
    blockchain_status = serializers.SerializerMethodField()
    can_store_blockchain = serializers.SerializerMethodField()
    formatted_trans_date = serializers.SerializerMethodField()
    formatted_trans_money = serializers.SerializerMethodField()
    short_tx_hash = serializers.SerializerMethodField()
    short_blockchain_hash = serializers.SerializerMethodField()
    
    class Meta:
        model = Audit
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_blockchain_status(self, obj):
        """获取区块链状态"""
        if obj.tx_hash and obj.blockchain_hash:
            return '已上链'
        elif obj.calculated_hash and not obj.blockchain_hash:
            return '已计算哈希，未上链'
        else:
            return '未处理'
    
    def get_can_store_blockchain(self, obj):
        """检查是否可以存储到区块链"""
        required_fields = ['trans_date', 'trans_money', 'card_number', 'trans_type']
        for field in required_fields:
            if not getattr(obj, field, None):
                return False
        return True
    
    def get_formatted_trans_date(self, obj):
        """格式化交易日期"""
        if obj.trans_date:
            return obj.trans_date.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_formatted_trans_money(self, obj):
        """格式化交易金额"""
        if obj.trans_money:
            return f"¥{obj.trans_money:,.2f}"
        return None
    
    def get_short_tx_hash(self, obj):
        """获取缩短的交易哈希"""
        if obj.tx_hash:
            return f"{obj.tx_hash[:16]}..."
        return None
    
    def get_short_blockchain_hash(self, obj):
        """获取缩短的区块链哈希"""
        if obj.blockchain_hash:
            return f"{obj.blockchain_hash[:16]}..."
        return None