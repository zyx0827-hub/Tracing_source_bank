from rest_framework import serializers
from .models import Announcements
import os
from django.conf import settings
from rest_framework import serializers
from apps.announcement.models import Announcements

class AnnouncementsSerializer(serializers.ModelSerializer):
    # 新增：用于接收上传文件的字段（只写）
    detail_attachment_file = serializers.FileField(
        write_only=True,
        required=False,
        allow_null=True,
        max_length=None,
        help_text='详情附件（支持PDF、Word格式，最大10MB）'
    )
    
    # 新增：返回给前端的完整URL（只读）
    detail_attachment_url = serializers.SerializerMethodField(read_only=True)
    
    # 新增：发布人名称（如果需要显示）
    publisher_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Announcements
        fields = [
            'id', 'title', 'content', 
            'detail_attachment', 'detail_attachment_url', 'detail_attachment_file',
            'publisher_id', 'publisher_name', 'publish_time', 'status'
        ]
        # 移除 publish_time 或设置为空列表
        read_only_fields = []  # 空列表，或者只保留 ['id']
        
        extra_kwargs = {
            'detail_attachment': {'read_only': True},
            # 可以添加 publish_time 的额外配置
            'publish_time': {
                'required': False,  # 不是必填
                'allow_null': True,  # 允许null
            }
        }
    
    def get_detail_attachment_url(self, obj):
        """生成完整的附件URL"""
        if obj.detail_attachment:
            # 这里根据你的文件存储服务来构建URL
            # 假设使用MinIO/OSS，返回完整URL
            file_base_url = getattr(settings, 'FILE_BASE_URL', 'https://your-minio-domain.com/')
            return f"{file_base_url.rstrip('/')}/{obj.detail_attachment.lstrip('/')}"
        return None
    
    def get_publisher_name(self, obj):
        """获取发布人名称（需要根据你的用户模型调整）"""
        # 这里假设你有User模型，需要根据实际情况调整
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=obj.publisher_id)
            return user.username
        except:
            return str(obj.publisher_id)
    
    def validate_detail_attachment_file(self, value):
        """验证上传的文件"""
        if value:
            # 1. 文件大小验证（10MB）
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f'文件大小不能超过10MB，当前文件大小: {value.size / 1024 / 1024:.1f}MB'
                )
            
            # 2. 文件类型验证
            ext = os.path.splitext(value.name)[1].lower()
            allowed_extensions = ['.pdf', '.doc', '.docx']
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f'只支持 {", ".join(allowed_extensions)} 格式的文件'
                )
            
            # 3. 重命名文件（避免重名和安全问题）
            import uuid
            import time
            timestamp = int(time.time())
            random_str = uuid.uuid4().hex[:8]
            new_filename = f"announcement_{timestamp}_{random_str}{ext}"
            value.name = new_filename
        
        return value
    
    def create(self, validated_data):
        """创建公告时的文件处理"""
        # 1. 提取文件数据
        attachment_file = validated_data.pop('detail_attachment_file', None)
        
        # 2. 设置发布人ID（从请求中获取）
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['publisher_id'] = request.user.id
        
        # 3. 设置默认状态
        if 'status' not in validated_data:
            validated_data['status'] = Announcements.STATUS_NORMAL
        
        # 4. 创建公告
        announcement = Announcements(**validated_data)
        
        # 5. 处理文件上传（如果有）
        if attachment_file:
            # 调用文件上传服务
            file_path = self.upload_attachment_file(attachment_file)
            announcement.detail_attachment = file_path
        
        announcement.save()
        return announcement
    
    def update(self, instance, validated_data):
        """更新公告时的文件处理"""
        # 1. 提取文件数据
        attachment_file = validated_data.pop('detail_attachment_file', None)
        
        # 2. 处理新文件上传（如果有）
        if attachment_file:
            # 删除旧文件（如果存在）
            if instance.detail_attachment:
                self.delete_attachment_file(instance.detail_attachment)
            
            # 上传新文件
            file_path = self.upload_attachment_file(attachment_file)
            instance.detail_attachment = file_path
        
        # 3. 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def upload_attachment_file(self, file):
        """上传文件到MinIO/OSS（需要根据你的文件服务实现）"""
        # 这里需要调用你的文件上传服务
        # 返回文件在存储中的相对路径
        try:
            # 示例：调用文件上传服务
            # file_service = getattr(settings, 'FILE_UPLOAD_SERVICE', None)
            # if file_service:
            #     return file_service.upload(file, 'announcements')
            
            # 临时实现：返回模拟路径
            import time
            from datetime import datetime
            date_path = datetime.now().strftime('%Y/%m')
            return f"announcements/{date_path}/{file.name}"
            
        except Exception as e:
            raise serializers.ValidationError(f'文件上传失败: {str(e)}')
    
    def delete_attachment_file(self, file_path):
        """删除文件（需要根据你的文件服务实现）"""
        # 这里需要调用你的文件删除服务
        try:
            # 示例：调用文件删除服务
            # file_service = getattr(settings, 'FILE_UPLOAD_SERVICE', None)
            # if file_service and file_path:
            #     file_service.delete(file_path)
            pass
        except Exception as e:
            # 记录错误但不中断流程
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'删除文件失败: {file_path}, 错误: {str(e)}')