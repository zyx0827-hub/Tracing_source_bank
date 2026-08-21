from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.sysuser.views import SysUserViewSet
from django.urls import path
from .views import SysUserViewSet
router = DefaultRouter()
router.register('',SysUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    
]
