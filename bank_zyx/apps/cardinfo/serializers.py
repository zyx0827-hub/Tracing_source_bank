from rest_framework import serializers
from .models import CardInfo

class CardInfoSerializer(serializers.ModelSerializer):
    cur_type_display = serializers.ReadOnlyField(source='get_cur_type_display')
    open_date_formatted = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        model = CardInfo
        fields = [
            'card_id', 'cur_type', 'cur_type_display', 
            'open_date', 'open_date_formatted', 
            'open_money', 'balance', 'password', 
            'customer_id', 'is_active'
        ]
    
    def validate_card_id(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("卡号必须为数字")
        return value