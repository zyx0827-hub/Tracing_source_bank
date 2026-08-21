from django.shortcuts import render # type: ignore
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q # type: ignore
from django.http import JsonResponse # type: ignore
import json
import logging

from apps.sysuser.models import SysUser
from apps.sysuser.serializers import SysUserSerializer

# 创建日志记录器
logger = logging.getLogger(__name__)

# Create your views here.

def sysuser(request):
    """系统用户管理页面"""
    user_id = request.GET.get('user_id', '')
    user_name = request.GET.get('user_name', '')
    return render(request, 'sysuser.html', {
        'user_id': user_id,
        'user_name': user_name
    })

def login_page(request):
    """登录页面"""
    return render(request, 'login.html')

def index(request):
    """首页"""
    return render(request, 'index.html')

class SysUserViewSet(viewsets.ModelViewSet):
    """用户表视图集"""
    queryset = SysUser.objects.all()
    serializer_class = SysUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_name', 'email', 'mobile']

    @action(detail=False, methods=['post'], url_path='login')
    def user_login(self, request):
        """
        用户登录接口
        POST /api-sysuser/login/
        """
        try:
            # 解析请求数据
            data = json.loads(request.body)
            user_name = data.get('user_name', '').strip()
            password = data.get('password', '').strip()
            
            logger.info(f"登录尝试: 用户名={user_name}")
            
            # 参数验证
            if not user_name:
                return JsonResponse({
                    'success': False,
                    'error': '用户名不能为空'
                }, status=400)
                
            if not password:
                return JsonResponse({
                    'success': False,
                    'error': '密码不能为空'
                }, status=400)
            
            # 查询用户
            try:
                user = SysUser.objects.get(user_name=user_name)
                logger.info(f"找到用户: {user.user_id}")
            except SysUser.DoesNotExist:
                logger.warning(f"用户不存在: {user_name}")
                return JsonResponse({
                    'success': False,
                    'error': '用户不存在'
                }, status=404)
            
            # 验证密码
            if user.password != password:
                logger.warning(f"密码错误: {user_name}")
                return JsonResponse({
                    'success': False,
                    'error': '密码错误'
                }, status=401)
            
            logger.info(f"登录成功: {user_name} (ID: {user.user_id})")
            
            # 登录成功，返回用户信息和重定向URL
            response_data = {
                'success': True,
                'message': '登录成功',
                'user_id': user.user_id,
                'user_name': user.user_name,
                'redirect_url': f'/sysuser?user_id={user.user_id}&user_name={user.user_name}'
            }
            
            # 添加额外的用户信息
            if hasattr(user, 'email') and user.email:
                response_data['email'] = user.email
            if hasattr(user, 'role') and user.role:
                response_data['role'] = user.role
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            logger.error("JSON解析错误")
            return JsonResponse({
                'success': False,
                'error': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"登录异常: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'登录失败: {str(e)}'
            }, status=500)