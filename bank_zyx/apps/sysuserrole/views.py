from django.shortcuts import render
from django.db import transaction
# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.decorators import action
from apps.sysuserrole.models import SysUserRole
from apps.sysuserrole.serializers import SysUserRoleSerializer
class SysUserRoleViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = SysUserRole.objects.all()
    serializer_class = SysUserRoleSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def assign_roles(self, request):
        """分配角色给用户"""
        user_id = request.data.get('user_id')
        role_ids = request.data.get('role_ids', [])
        
        try:
            with transaction.atomic():
                # 删除用户现有的所有角色
                SysUserRole.objects.filter(user_id=user_id).delete()
                
                # 添加新的角色
                for role_id in role_ids:
                    SysUserRole.objects.create(
                        user_id=user_id,
                        role_id=role_id
                    )
                
                return Response({'message': '角色分配成功'}, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)