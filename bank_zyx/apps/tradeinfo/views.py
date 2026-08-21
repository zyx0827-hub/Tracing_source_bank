from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
# Create your views here.
from rest_framework import status
from rest_framework import viewsets,filters
from apps.tradeinfo.models import TradeInfo
from apps.tradeinfo.serializers import TradeInfoSerializer
class TradeInfoViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = TradeInfo.objects.all()
    serializer_class = TradeInfoSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # 添加过滤和排序支持
    search_fields = ['card_id',"remark"]  # 根据这些字段进行搜索

    @action(detail=False, methods=['get'], url_path='by-tid')
    def get_by_tid(self, request):
        """
        根据交易ID (tid) 获取交易信息
        
        参数:
            tid: 交易ID
        
        返回:
            对应的交易信息
        """
        tid = request.query_params.get('tid')
        
        if not tid:
            return Response({
                'success': False,
                'error': '请提供交易ID (tid) 参数',
                'message': '使用方式: /api-tradeinfo/by-tid/?tid=123'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 尝试将 tid 转换为整数
            tid_int = int(tid)
            
            # 查找对应的交易信息
            trade_info = TradeInfo.objects.get(tid=tid_int)
            
            # 使用序列化器返回数据
            serializer = self.get_serializer(trade_info)
            
            return Response({
                'success': True,
                'message': '获取交易信息成功',
                'trade_info': serializer.data
            })
            
        except ValueError:
            return Response({
                'success': False,
                'error': '交易ID格式错误，请输入数字',
                'tid': tid
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except TradeInfo.DoesNotExist:
            return Response({
                'success': False,
                'error': f'未找到交易ID为 {tid} 的交易信息',
                'tid': tid
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'获取交易信息时发生错误: {str(e)}',
                'tid': tid
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
