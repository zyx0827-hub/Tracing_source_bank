# 修改文件atis/apps/sysadmin/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 导入视图集
from apps.tradeinfo.views import TradeInfoViewSet
# 使用router生成路径相关
router = DefaultRouter()
# 将视图集注册到路由模块生成路径
router.register('',TradeInfoViewSet, basename='tradeinfo')
# 在列表中添加
urlpatterns = [
    path('',include(router.urls)),
]