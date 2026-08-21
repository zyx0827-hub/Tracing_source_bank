from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CardInfo
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CardInfoSerializer
from rest_framework import viewsets,filters
from django.db import transaction

class CardInfoViewSet(viewsets.ModelViewSet):
    queryset = CardInfo.objects.all()
    serializer_class = CardInfoSerializer
    lookup_field = 'card_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # 添加过滤和排序支持
    # 修正搜索字段 - 使用模型中实际存在的字段
    search_fields = ['card_id']  # 根据你的模型字段调整
    
    # 排序字段配置
    ordering_fields = ['card_id']

    def list(self, request):
        cards = CardInfo.objects.all()
        serializer = self.get_serializer(cards, many=True)
        return Response({
            'count': cards.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_cards = CardInfo.objects.count()
        total_balance = sum(card.balance for card in CardInfo.objects.all())
        active_cards = CardInfo.objects.filter(is_active=True).count()
        return Response({
            'total_cards': total_cards,
            'total_balance': float(total_balance),
            'active_cards': active_cards
        })
    
    
    def create(self, request, *args, **kwargs):
                """
                重写create方法，在创建银行卡后自动创建存款交易记录
                """
                try:
                    with transaction.atomic():
                        # 调用父类的create方法创建银行卡
                        response = super().create(request, *args, **kwargs)
                        
                        if response.status_code == status.HTTP_201_CREATED:
                            # 获取创建的银行卡数据
                            card_data = response.data
                            card_id = card_data.get('card_id')
                            open_money = float(card_data.get('open_money', 0))
                            
                            # 只有在开户金额大于0时才创建存款交易
                            if open_money > 0:
                                # 创建存款交易记录
                                transaction_created = self._create_deposit_transaction(card_id, open_money)
                                
                                if transaction_created:
                                    # 在响应中添加交易创建信息
                                    response.data['transaction_created'] = True
                                    response.data['transaction_message'] = f'已自动创建开户存款交易，金额: {open_money}'
                                else:
                                    response.data['transaction_created'] = False
                                    response.data['transaction_message'] = '创建存款交易失败'
                            else:
                                response.data['transaction_created'] = False
                                response.data['transaction_message'] = '开户金额为0，未创建存款交易'
                        
                        return response
                        
                except Exception as e:
                    return Response({
                        'error': f'创建银行卡失败: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
    def _create_deposit_transaction(self, card_id, amount):
            """
            创建存款交易记录到trade_info表
            """
            try:
                from django.db import connection
                from django.utils import timezone
                
                # 获取当前时间
                current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 生成新的交易ID
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COALESCE(MAX(tid), 0) FROM trade_info")
                    max_tid = cursor.fetchone()[0]
                    new_tid = max_tid + 1
                
                # 插入存款交易记录
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO trade_info (tid, trans_type, card_id, trans_date, trans_money, remark)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, [
                        new_tid,
                        '存款',  # trans_type
                        card_id,  # card_id
                        current_time,  # trans_date
                        amount,  # trans_money
                        '开户存款'  # remark
                    ])
                
                return True
                
            except Exception as e:
                print(f"创建存款交易失败: {str(e)}")
                return False

            

            return super().create(request, *args, **kwargs)