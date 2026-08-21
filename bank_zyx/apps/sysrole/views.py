from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import viewsets,filters
from apps.sysrole.models import SysRole
from apps.sysrole.serializers import SysRoleSerializer
class SysRoleViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = SysRole.objects.all()
    serializer_class = SysRoleSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # 添加过滤和排序支持
    search_fields = ['role_id',"role_name",'description']  # 错误拼写  # 根据这些字段进行搜索
