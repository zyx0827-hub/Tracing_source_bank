
# 修改文件atis/apps/sysadmin/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 导入视图集
from apps.announcement.views import AnnouncementsViewSet
# 使用router生成路径相关
router = DefaultRouter()
# 将视图集注册到路由模块生成路径
router.register('',AnnouncementsViewSet, basename='announcement')
# 在列表中添加
urlpatterns = [
    path('', include(router.urls)),
    
    # 可选：添加直接访问的路径
    path('admin/list/', AnnouncementsViewSet.as_view({'get': 'admin_list'}), 
         name='announcement-admin-list'),
    path('user/list/', AnnouncementsViewSet.as_view({'get': 'user_list'}), 
         name='announcement-user-list'),
    path('<int:pk>/user/', AnnouncementsViewSet.as_view({'get': 'user_detail'}), 
         name='announcement-user-detail'),
    path('<int:pk>/admin/', AnnouncementsViewSet.as_view({'get': 'admin_detail'}), 
         name='announcement-admin-detail'),
    path('<int:pk>/upload-attachment/', 
         AnnouncementsViewSet.as_view({'post': 'upload_attachment'}), 
         name='announcement-upload-attachment'),
]