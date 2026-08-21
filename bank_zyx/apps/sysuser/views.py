from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.sysuser.models import SysUser
from apps.sysuser.serializers import SysUserSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from apps.sysrole.models import SysRole  # 导入角色模型
from rest_framework import viewsets, status

class SysUserViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = SysUser.objects.all()
    serializer_class = SysUserSerializer
    
    # 定义过滤后端和搜索字段
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_id', 'user_name', 'pid', 'email', 'mobile', 'address']

    # 登录接口
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        用户登录接口
        POST /api-user/api-user/login/
        """
        print("=== 登录接口被调用 ===")
        print("请求数据:", request.data)
        
        username = request.data.get('user_name')
        password = request.data.get('password')

        try:
            user = SysUser.objects.get(user_name=username, password=password)
            print(f"登录成功: {user.user_name} (ID: {user.user_id})")
            
            return Response({
                "success": True,
                "message": "登录成功",
                "user_id": user.user_id,
                "user_name": user.user_name
            })
        except SysUser.DoesNotExist:
            print(f"登录失败: 用户不存在或密码错误 - {username}")
            return Response({
                "success": False,
                "message": "用户名或密码错误"
            }, status=status.HTTP_401_UNAUTHORIZED)