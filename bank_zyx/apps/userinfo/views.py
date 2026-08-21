from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from rest_framework import viewsets,filters
from apps.userinfo.models import UserInfo
from apps.userinfo.serializers import UserInfoSerializer
class UserInfoViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # 添加过滤和排序支持
    search_fields = ['customer_id',"customer_name",'address']  # 根据这些字段进行搜索
