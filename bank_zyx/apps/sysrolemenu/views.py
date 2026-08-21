

from rest_framework import viewsets  # 修正导入
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.sysrolemenu.models import SysRoleMenu
from apps.sysrole.models import SysRole
from apps.sysmenu.models import SysMenu
from apps.sysrolemenu.serializers import SysRoleMenuSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
class SysRoleMenuViewSet(viewsets.ModelViewSet):
    """角色菜单视图集"""  # 修正注释
    queryset = SysRoleMenu.objects.all()
    serializer_class = SysRoleMenuSerializer
    
    @action(detail=False, methods=['post'], url_path='bulk_assign')
    def bulk_assign(self, request):
        """
        批量分配菜单给角色
        POST /api-rolemenu/bulk_assign/
        {
            "role_id": 1,
            "menu_ids": [1, 2, 3, 4]
        }
        """
        try:
            role_id = request.data.get('role_id')
            menu_ids = request.data.get('menu_ids', [])
            
            if not role_id:
                return Response({
                    'error': 'role_id 是必需的'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证角色是否存在
            try:
                role = SysRole.objects.get(role_id=role_id)
            except SysRole.DoesNotExist:
                return Response({
                    'error': '角色不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 验证菜单是否存在
            existing_menus = SysMenu.objects.filter(menu_id__in=menu_ids)
            existing_menu_ids = set(existing_menus.values_list('menu_id', flat=True))
            
            invalid_menu_ids = set(menu_ids) - existing_menu_ids
            if invalid_menu_ids:
                return Response({
                    'error': f'以下菜单ID不存在: {list(invalid_menu_ids)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # 删除该角色现有的所有菜单关联
                SysRoleMenu.objects.filter(role_id=role_id).delete()
                
                # 创建新的菜单关联
                role_menus = []
                for menu_id in menu_ids:
                    role_menus.append(SysRoleMenu(
                        role_id=role_id,
                        menu_id=menu_id
                    ))
                
                if role_menus:
                    SysRoleMenu.objects.bulk_create(role_menus)
            
            return Response({
                'success': True,
                'message': f'成功为角色 {role.role_name} 分配了 {len(menu_ids)} 个菜单',
                'assigned_count': len(menu_ids)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'分配菜单失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='get_role_menus')
    def get_role_menus(self, request):
        """
        获取角色已分配的菜单ID列表
        GET /api-rolemenu/get_role_menus/?role_id=1
        """
        try:
            role_id = request.GET.get('role_id')
            
            if not role_id:
                return Response({
                    'error': 'role_id 参数是必需的'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取角色已分配的菜单ID
            role_menus = SysRoleMenu.objects.filter(role_id=role_id)
            menu_ids = list(role_menus.values_list('menu_id', flat=True))
            
            return Response({
                'role_id': int(role_id),
                'menu_ids': menu_ids,
                'count': len(menu_ids)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'获取角色菜单失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)