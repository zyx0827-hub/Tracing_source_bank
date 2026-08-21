from django.shortcuts import render
from rest_framework import viewsets, status
# Create your views here.
from rest_framework import viewsets,filters
from rest_framework.decorators import action
from apps.sysmenu.models import SysMenu
from apps.sysuser.models import SysUser
from apps.sysuserrole.models import SysUserRole
from apps.sysrolemenu.models import SysRoleMenu
from apps.sysmenu.serializers import SysMenuSerializer
from rest_framework.response import Response
class SysMenuViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = SysMenu.objects.all()
    serializer_class = SysMenuSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # 添加过滤和排序支持
    search_fields = ['menu_id',"menu_name"]  # 根据这些字段进行搜索
    

    #根据用户ID获取该用户有权限访问的菜单
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_menus(self, request, user_id=None):

        """
        根据用户ID获取该用户有权限访问的菜单
        GET /api-menu/user/{user_id}/
        """
        print("--------------------- user_id = ",user_id)
        try:
            # 验证用户是否存在
            try:
                user = SysUser.objects.get(user_id=user_id)
            except SysUser.DoesNotExist:
                return Response(
                    {'error': '用户不存在'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 1 获取用户的所有角色
            user_roles = SysUserRole.objects.filter(user_id=user_id)
            role_ids = list(user_roles.values_list('role_id', flat=True))
            
            if not role_ids:
                # 用户没有分配角色，返回空菜单
                return Response({
                    'user_id': int(user_id),
                    'user_name': user.user_name,
                    'menus': [],
                    'count': 0
                })
            
            # 获取这些角色对应的菜单ID
            role_menus = SysRoleMenu.objects.filter(role_id__in=role_ids)
            menu_ids = list(role_menus.values_list('menu_id', flat=True))
            
            if not menu_ids:
                # 角色没有分配菜单，返回空菜单
                return Response({
                    'user_id': int(user_id),
                    'user_name': user.user_name,
                    'menus': [],
                    'count': 0
                })
            
            # 获取菜单数据，按排序字段排序
            menus = SysMenu.objects.filter(
                menu_id__in=menu_ids
            )
            
            serializer = self.get_serializer(menus, many=True)
            return Response({
                'user_id': int(user_id),
                'user_name': user.user_name,
                'menus': serializer.data,
                'count': len(menus)
            })
            
        except Exception as e:
            return Response(
                {'error': f'获取用户菜单失败: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        


        