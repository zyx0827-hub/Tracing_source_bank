from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
# Create your views here.
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets,filters
from apps.announcement.models import Announcements
from apps.announcement.serializers import AnnouncementsSerializer
class AnnouncementsViewSet(viewsets.ModelViewSet):
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # 添加过滤和排序支持
    search_fields = ['publisher_id', 'title']  # 根据这些字段进行搜索
    
    def get_queryset(self):
        """根据action过滤数据"""
        queryset = Announcements.objects.all()
        
        # 用户端接口只返回正常状态的公告
        if self.action in ['list', 'retrieve', 'user_list', 'user_detail']:
            queryset = queryset.filter(status=Announcements.STATUS_NORMAL)
        
        # 管理端接口返回所有公告
        elif self.action in ['admin_list', 'admin_detail']:
            pass  # 返回全部
        
        return queryset
    
    def get_serializer_context(self):
        """传递request到serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_destroy(self, instance):
        """重写删除方法：软删除+删除附件文件"""
        # 1. 删除附件文件
        if instance.detail_attachment:
            try:
                # 这里需要调用文件删除服务
                # file_service.delete(instance.detail_attachment)
                pass
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'删除公告附件失败: {instance.detail_attachment}, 错误: {str(e)}')
        
        # 2. 软删除（更新状态为0）
        instance.status = Announcements.STATUS_DELETED
        instance.save()
    
    @action(detail=False, methods=['get'])
    def admin_list(self, request):
        """管理端列表（包含已删除的公告）"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def admin_detail(self, request, pk=None):
        """管理端详情（包含已删除的公告）"""
        try:
            announcement = Announcements.objects.get(pk=pk)
        except Announcements.DoesNotExist:
            return Response({'error': '公告不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(announcement)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_list(self, request):
        """用户端列表（只返回必要字段，不包含附件URL）"""
        queryset = self.get_queryset()
        # 只返回基本字段，避免包含附件信息
        data = queryset.values('id', 'title', 'publish_time')
        return Response(list(data))
    
    @action(detail=True, methods=['get'])
    def user_detail(self, request, pk=None):
        """用户端详情（返回完整信息，包含附件URL）"""
        try:
            announcement = self.get_queryset().get(pk=pk)
        except Announcements.DoesNotExist:
            return Response({'error': '公告不存在或已被删除'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(announcement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        """单独上传附件（如果需要）"""
        try:
            announcement = self.get_object()
        except Announcements.DoesNotExist:
            return Response({'error': '公告不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'detail_attachment_file' not in request.FILES:
            return Response({'error': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['detail_attachment_file']
        
        # 验证文件
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.pdf', '.doc', '.docx']:
            return Response({'error': '只支持PDF和Word格式'}, status=status.HTTP_400_BAD_REQUEST)
        
        if file.size > 10 * 1024 * 1024:
            return Response({'error': '文件大小不能超过10MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 处理文件上传
        try:
            # 删除旧文件（如果存在）
            if announcement.detail_attachment:
                # 调用文件删除服务
                pass
            
            # 上传新文件
            import uuid
            import time
            timestamp = int(time.time())
            random_str = uuid.uuid4().hex[:8]
            new_filename = f"announcement_{timestamp}_{random_str}{ext}"
            
            # 调用文件上传服务
            # file_path = file_service.upload(file, 'announcements', new_filename)
            file_path = f"announcements/{timestamp}_{random_str}{ext}"
            
            # 更新数据库
            announcement.detail_attachment = file_path
            announcement.save()
            
            return Response({
                'success': True,
                'detail_attachment_url': f"https://your-minio-domain.com/{file_path}"
            })
            
        except Exception as e:
            return Response({'error': f'文件上传失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """重写create方法，支持multipart/form-data"""
        # 检查是否是multipart/form-data格式
        if request.content_type.startswith('multipart/form-data'):
            # 从request.data中获取数据
            data = request.data.copy()
            
            # 处理文件字段
            if 'detail_attachment_file' in request.FILES:
                data['detail_attachment_file'] = request.FILES['detail_attachment_file']
            
            serializer = self.get_serializer(data=data)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementsSerializer

